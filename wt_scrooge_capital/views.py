# By: Tsz Kit Wong
# File: wt_scrooge_capital/views.py

# views for the wt_scrooge_capital app


from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from .models import Transaction, UserProfile, Portfolio, WatchList, Stock, StockPriceHistory
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from .forms import BuySellForm, CustomAuthenticationForm, SignupForm
from django.views.generic.edit import FormView
import plotly.express as px
from plotly.io import to_html
import datetime


class CustomLoginView(auth_views.LoginView):
    """
        Custom login view
    """
    authentication_form = CustomAuthenticationForm
    template_name = 'wt_scrooge_capital/login.html'


class HomeView(LoginRequiredMixin, ListView):
    """
        Create a subclass of ListView
    """
    model = Stock
    template_name = 'wt_scrooge_capital/home.html'
    context_object_name = 'stocks'


    def get_context_data(self, **kwargs):
        """
            get the context data for the home page
        """
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['profile'] = user_profile
        context['stocks'] = Stock.objects.all()
        return context
     

class PortfolioView(LoginRequiredMixin, ListView):
    """
        Displays the user's portfolio.
    """
    model = Portfolio
    template_name = 'wt_scrooge_capital/portfolio.html'
    context_object_name = 'portfolio'


    def get_queryset(self):
        """
            gets the queryset for the portfolio
        """
        user_profile = UserProfile.objects.get(user=self.request.user)
        return Portfolio.objects.filter(user=user_profile)


    def get_context_data(self, **kwargs):
        """
            gets the context data for the portfolio
        """
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        portfolio_items = Portfolio.objects.filter(user=user_profile)

        # calculate the total value of each stock in the portfolio
        for item in portfolio_items:
            item.total_value = item.shares * item.stock.current_price
        
        context['portfolio'] = portfolio_items

        # calculate the total value of the portfolio based on the current price of the stocks and the number of shares
        context['portfolio_total_shares'] = sum(item.shares for item in portfolio_items)
        context['portfolio_total_value'] = sum(item.shares * item.stock.current_price for item in portfolio_items)
        context['buy_sell_form'] = BuySellForm()
        return context
    

    def post(self, request, *args, **kwargs):
        """
            handles the buy/sell form submission
        """
        form = BuySellForm(request.POST)
        user_profile = UserProfile.objects.get(user=request.user)
        
        if form.is_valid():
            stock = form.cleaned_data['stock']
            action = form.cleaned_data['action']
            shares = form.cleaned_data['shares']

            # get the portfolio item for the stock if it exists, otherwise create a new one
            portfolio_item, created = Portfolio.objects.get_or_create(user=user_profile, stock=stock, defaults={
                'shares': 0,
                'purchase_price': stock.current_price,
                'purchase_date': datetime.date.today(),
            })

            # check if the user has enough shares to sell, if not, redirect to the portfolio page
            if action == 'buy':
                portfolio_item.shares += shares
                portfolio_item.purchase_price = stock.current_price

                # update the transaction history
                Transaction.objects.create(
                    user=user_profile,
                    stock=stock,
                    shares=shares,
                    purchase_price=stock.current_price,
                    purchase_date=datetime.date.today(),
                    transaction_type='buy',
                )
            elif action == 'sell':
                if portfolio_item.shares == 0:
                    portfolio_item.delete()

                    return redirect(reverse('portfolio'))
                
                if portfolio_item.shares >= shares:
                    portfolio_item.shares -= shares

                    if portfolio_item.shares == 0:
                        portfolio_item.delete()
                        return redirect(reverse('portfolio'))
                    
                    # update the transaction history   
                    Transaction.objects.create(
                        user=user_profile,
                        stock=stock,
                        shares=shares,
                        purchase_price=stock.current_price,
                        purchase_date=datetime.date.today(),
                        transaction_type='sell',
                    )
                    
                else:
                    return redirect(reverse('portfolio'))

            portfolio_item.save()
            return redirect(reverse('portfolio'))

        return redirect(reverse('portfolio'))


class WatchlistView(LoginRequiredMixin, ListView):
    """
        Displays the user's watchlist
    """
    model = WatchList
    template_name = 'wt_scrooge_capital/watchlist_expanded.html'
    context_object_name = 'watchlist'


    def get_queryset(self):
        """
            gets the queryset for the watchlist
        """
        user_profile = UserProfile.objects.get(user=self.request.user)
        return WatchList.objects.filter(user=user_profile)


    def get_context_data(self, **kwargs):
        """
            gets the context data for the watchlist
        """
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['profile'] = user_profile
        return context

    
class TransactionsView(LoginRequiredMixin, ListView):
    """
        Displays the transaction history for the logged-in user.
    """
    model = Transaction
    template_name = 'wt_scrooge_capital/transactions_list.html'
    context_object_name = 'transactions'


    def get_queryset(self):
        """
            gets the queryset for the transaction history
        """
        user_profile = UserProfile.objects.get(user=self.request.user)
        return Transaction.objects.filter(user=user_profile)


    def get_context_data(self, **kwargs):
        """
            gets the context data for the transaction history
        """
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['profile'] = user_profile
        return context


class ProfileView(LoginRequiredMixin, ListView):
    """
        Displays the profile page for the logged-in user.
    """
    model = UserProfile
    template_name = 'wt_scrooge_capital/profile.html'
    context_object_name = 'profile'


    def get_queryset(self):
        """
            gets the queryset for the profile
        """
        return UserProfile.objects.filter(user=self.request.user)


    def get_context_data(self, **kwargs):
        """
            gets the context data for the profile
        """
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context['profile'] = user_profile
        context['stocks'] = Stock.objects.all()
        context['transactions'] = Transaction.objects.filter(user=user_profile)
        return context


class SignupView(FormView):
    """
        View for user registration
    """
    template_name = 'wt_scrooge_capital/signup.html'
    form_class = SignupForm
    success_url = '/'


    def form_valid(self, form):
        """
            handle the form submission
        """
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)
    

class StockDetailView(LoginRequiredMixin, DetailView):
    """
        Detailed view of a single Stock record, including price history and graphs.
    """
    model = Stock
    template_name = 'wt_scrooge_capital/stock_detail.html'
    context_object_name = 'stock'


    def get_context_data(self, **kwargs):
        """
            get the context data for the stock detail page
        """
        context = super().get_context_data(**kwargs)
        stock = self.object
        price_history_record = StockPriceHistory.objects.filter(stock=stock).first()

        # get the fields from the StockPriceHistory model to display on the stock detail page's graphs
        if price_history_record and price_history_record.price_history:
            price_history = [
                float(price.strip()) for price in price_history_record.price_history.strip("[]").split(",")
            ]
            hours = [f"{hour}:00" for hour in range(1, len(price_history) + 1)]
            line_color = 'rgb(0, 200, 5)' if price_history[-1] > price_history[0] else 'rgb(255, 80, 0)'

            price_chart = px.line(
                x=hours,
                y=price_history,
                labels={"x": "Hour", "y": "Price ($)"},
                title=f"{stock.company_name} ({stock.ticker}) - 12-Hour Price History",
            )
            price_chart.update_traces(
                mode="lines+markers",
                line=dict(color=line_color),
            )
            price_chart.update_layout(
                width=900,
                height=600,
                # plot_bgcolor="rgba(30, 30, 30, 1)",
                title_font=dict(size=18),
                xaxis_title_font=dict(size=14),
                yaxis_title_font=dict(size=14),
            )

            # add the fields to the context
            context['open_price'] = price_history_record.open_price
            context['close_price'] = price_history_record.close_price
            context['region'] = price_history_record.region
            context['type'] = price_history_record.type
            context['price_chart'] = to_html(price_chart, full_html=False)
            context['max_price'] = max(price_history)
            context['min_price'] = min(price_history)
            context['diff'] = context['close_price'] - context['open_price']

        if self.request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=self.request.user)
            portfolio_item = Portfolio.objects.filter(user=user_profile, stock=stock).first()
            context['shares_owned'] = portfolio_item.shares if portfolio_item else 0
        else:
            context['shares_owned'] = 0

        return context


class StockListView(LoginRequiredMixin, ListView):
    """
        Displays all stocks
    """
    model = Stock
    template_name = 'wt_scrooge_capital/all_stocks.html'
    context_object_name = 'stocks'
    paginate_by = 3  # number of stocks per page


class RemoveFromWatchlistView(LoginRequiredMixin, View):
    """
        Handles the removal of an item from the watchlist
    """
    def post(self, request, pk):
        """
            method for removing an item from the watchlist
        """
        user_profile = UserProfile.objects.get(user=request.user)
        watchlist_item = get_object_or_404(WatchList, pk=pk, user=user_profile)
        watchlist_item.delete()
        return HttpResponseRedirect(reverse('watchlist'))
    

class AddToWatchlistView(LoginRequiredMixin, View):
    """
        Handles adding a stock to the user's watchlist
    """
    def post(self, request, stock_id):
        """
            method for adding a stock to the watchlist
        """
        user_profile = UserProfile.objects.get(user=request.user)
        stock = get_object_or_404(Stock, id=stock_id)

        # check if the stock is already in the user's watchlist, if not then add it
        if not WatchList.objects.filter(user=user_profile, stock=stock).exists():
            WatchList.objects.create(
                user=user_profile,
                stock=stock,
                added_price=stock.current_price,
                current_price=stock.current_price
            )
        return redirect(reverse('stock_list'))