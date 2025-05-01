from datetime import timezone
from pyexpat.errors import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from collections import defaultdict

from kort import settings
from .models import Player, Season, Game

class PlayerListView(ListView):
    model = Player
    queryset = Player.objects.all().order_by('name')
    template_name = 'ristiseiska/player_list.html'  # Explicit template path


class PlayerCreateView(CreateView):
    model = Player
    fields = ('name',)
    success_url = reverse_lazy('player_list')
    template_name = 'ristiseiska/player_create.html'  # Explicit template path


class PlayerUpdateView(UpdateView):
    model = Player
    fields = ('name',)
    success_url = reverse_lazy('player_list')
    template_name = 'ristiseiska/player_update.html'  # Explicit template path


class PlayerDeleteView(DeleteView):
    model = Player
    success_url = reverse_lazy('player_list')
    template_name = 'ristiseiska/player_delete.html'  # Explicit template path


class SeasonListView(ListView):
    model = Season
    template_name = 'ristiseiska/season_list.html'  # Explicit template path

    def get_queryset(self):
        # Order seasons by start_date (descending) to align with template
        return Season.objects.all().order_by('-start_date')

    def get_current_season(self):
        # Return the season with the highest id, or None if no seasons exist
        try:
            return Season.objects.all().order_by('-id').first()
        except IndexError:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_season = self.get_current_season()
        if current_season:
            context['leaderboard'] = get_leaderboard_for_season(current_season.id)
        else:
            context['leaderboard'] = {
                'season_id': None,
                'season_name': '',
                'season_start_date': None,
                'players': []
            }
        return context


class SeasonCreateView(CreateView):
    model = Season
    fields = ('name', 'start_date', 'end_date')
    success_url = reverse_lazy('season_list')
    template_name = 'ristiseiska/season_create.html'  # Explicit template path


class SeasonUpdateView(UpdateView):
    model = Season
    fields = ('name', 'start_date', 'end_date')
    success_url = reverse_lazy('season_list')
    template_name = 'ristiseiska/season_update.html'  # Explicit template path


class SeasonDeleteView(DeleteView):
    model = Season
    success_url = reverse_lazy('season_list')
    template_name = 'ristiseiska/season_delete.html'  # Explicit template path


class GameListView(ListView):
    model = Game
    template_name = 'ristiseiska/game_list.html'
    context_object_name = 'games'

    def get_queryset(self):
        """
        Palauttaa vain nykyisen kauden pelit.
        """
        latest_season = Season.objects.order_by('-start_date').first()
        if latest_season:
            return Game.objects.filter(season=latest_season)
        else:
            return Game.objects.none()  # Palauttaa tyhjän kyselyjoukon, jos kausia ei ole.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Hae viimeisin kausi ja välitä se templaatille
        latest_season = Season.objects.order_by('-start_date').first()
        context['current_season'] = latest_season
        return context

class GameCreateView(CreateView):
    model = Game
    fields = ('winner', 'loser') # Removed 'season' from fields
    success_url = reverse_lazy('game_list')
    template_name = 'ristiseiska/game_create.html'

    def form_valid(self, form):
        """
        Override the form_valid method to set the season automatically.
        """
        # Get the latest season
        latest_season = Season.objects.order_by('-start_date').first()
        if latest_season:
            form.instance.season = latest_season
        else:
            # Handle the case where there are no seasons.  This is important!
            # You might want to create a default season, or raise an error.
            # Here, I'm choosing to create a new season if none exists.
            new_season = Season.objects.create(name="Default Season", start_date=timezone.now()) #Added import
            form.instance.season = new_season

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the latest season to the template for display, if needed
        latest_season = Season.objects.order_by('-start_date').first()
        context['latest_season'] = latest_season
        return context
    
class GameUpdateView(UpdateView):
    model = Game
    fields = ('winner', 'loser', 'date', 'season')
    success_url = reverse_lazy('game_list')
    template_name = 'ristiseiska/game_update.html'  # Explicit template path

class SeasonDetailView(DetailView):
    model = Season
    template_name = 'ristiseiska/season_detail.html'  # Default: season_detail.html
    context_object_name = 'season'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        season = self.get_object()
        context['leaderboard'] = get_leaderboard_for_season(season.id)
        return context
    
class GameDeleteView(DeleteView):
    model = Game
    success_url = reverse_lazy('game_list')
    template_name = 'ristiseiska/game_delete.html' 
    
    
def check_password(request):
  """
  View to check the password against the value in settings.py.
  Returns a JSON response.
  """
  if request.method == "POST":
    entered_password = request.POST.get("password", "")
    correct_password = settings.PASSWORD_PROTECTION  # Get from settings
    if entered_password == correct_password:
      return JsonResponse({"valid": True})
    else:
      return JsonResponse({"valid": False})
  else:
    return JsonResponse({"error": "Invalid request method"}, status=400)
  
def get_leaderboard_for_season(season_id):
    # Initialize a dictionary to store results
    stats = {}
    
    # Query to get wins for the specified season
    wins = (Game.objects
            .filter(season__id=season_id)
            .values('season__id', 'season__name', 'season__start_date', 'winner__id', 'winner__name')
            .annotate(wins=Count('id'))
            .order_by('winner__name'))
    
    # Query to get losses for the specified season
    losses = (Game.objects
              .filter(season__id=season_id)
              .values('season__id', 'season__name', 'season__start_date', 'loser__id', 'loser__name')
              .annotate(losses=Count('id'))
              .order_by('loser__name'))
    
    # Process wins
    for win in wins:
        season_id = win['season__id']
        season_name = win['season__name']
        season_start_date = win['season__start_date']
        player_id = win['winner__id']
        player_name = win['winner__name']
        wins_count = win['wins']
        
        stats[player_id] = stats.get(player_id, {
            'season_name': season_name,
            'season_start_date': season_start_date,
            'player_name': player_name,
            'wins': 0,
            'losses': 0,
            'total': 0
        })
        stats[player_id]['wins'] = wins_count
        stats[player_id]['total'] += wins_count  # +1 per win
    
    # Process losses
    for loss in losses:
        season_id = loss['season__id']
        season_name = loss['season__name']
        season_start_date = loss['season__start_date']
        player_id = loss['loser__id']
        player_name = loss['loser__name']
        losses_count = loss['losses']
        
        stats[player_id] = stats.get(player_id, {
            'season_name': season_name,
            'season_start_date': season_start_date,
            'player_name': player_name,
            'wins': 0,
            'losses': 0,
            'total': 0
        })
        stats[player_id]['losses'] = losses_count
        stats[player_id]['total'] -= losses_count  # -1 per loss
    
    # Convert to leaderboard format with ranking
    # Sort players by total score (descending) and then by player_name (ascending) for ties
    sorted_players = sorted(
        stats.items(),
        key=lambda x: (-x[1]['total'], x[1]['player_name'])
    )
    
    # Assign ranks
    season_players = []
    current_rank = 1
    previous_total = None
    for index, (player_id, data) in enumerate(sorted_players):
        if previous_total is not None and data['total'] < previous_total:
            current_rank = index + 1
        season_players.append({
            'rank': current_rank,
            'player_id': player_id,
            'player_name': data['player_name'],
            'wins': data['wins'],
            'losses': data['losses'],
            'total': data['total']
        })
        previous_total = data['total']
    
    # Return result for the season
    if not stats:
        return {
            'season_id': season_id,
            'season_name': '',
            'season_start_date': None,
            'players': []
        }
    
    return {
        'season_id': season_id,
        'season_name': stats[sorted_players[0][0]]['season_name'],
        'season_start_date': stats[sorted_players[0][0]]['season_start_date'],
        'players': season_players
    }