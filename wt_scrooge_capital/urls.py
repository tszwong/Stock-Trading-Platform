# By: Tsz Kit Wong
# File wt_scrooge_capital/urls.py

# contains the URL patterns for the wt_scrooge_capital app


from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import AddToWatchlistView, CustomLoginView, HomeView, PortfolioView, RemoveFromWatchlistView, SignupView, \
                   StockDetailView, StockListView, WatchlistView, TransactionsView, ProfileView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    path('watchlist/', WatchlistView.as_view(), name='watchlist'),
    path('transactions/', TransactionsView.as_view(), name='transactions'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('stock/<int:pk>/graphs/', StockDetailView.as_view(), name='stock_detail'),
    path('stocks/', StockListView.as_view(), name='stock_list'),
    path('watchlist/remove/<int:pk>/', RemoveFromWatchlistView.as_view(), name='remove_from_watchlist'),
    path('add-to-watchlist/<int:stock_id>/', AddToWatchlistView.as_view(), name='add_to_watchlist'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='wt_scrooge_capital/logged_out.html'), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
]