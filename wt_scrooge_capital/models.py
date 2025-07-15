# By: Tsz Kit Wong
# File: wt_scrooge_capital/models.py

# Models of the app


from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    """
        User profile model to store additional user information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    dob = models.DateField(null=True, blank=True)


    def __str__(self):
        """
            return the full name of the user
        """
        return f"{self.first_name} {self.last_name}"


class Stock(models.Model):
    """
        Stock model to store stock information
    """
    ticker = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        """
            return the company name, ticker, and current price of the stock
        """
        return f"{self.company_name}, ({self.ticker}), current_price: ${self.current_price}"
    

class StockPriceHistory(models.Model):
    """
        Stock price history model to store additional information about the stock
    """
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="price_history")
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    region = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    price_history = models.TextField(blank=False, default="")


    def get_price_history(self):
        """"
            return the price history of the stock
        """
        return [float(price) for price in self.price_history.split(",") if price]


    def __str__(self):
        """
            return the stock ticker, date, open price, and close price  
        """
        return f"{self.stock.ticker} on {self.date}, open_price: ${self.open_price}, close_price: ${self.close_price}"


class Portfolio(models.Model):
    """
        Portfolio model to store user's portfolio information
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="portfolio")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()


    def get_context_data(self, **kwargs):
        """
            return the context data of the portfolio
        """

        context = super().get_context_data(**kwargs)
        user_profile = self.get_object()
        portfolio_items = Portfolio.objects.filter(user=user_profile)
        
        context['portfolio'] = portfolio_items
        context['profile'] = user_profile
        context['portfolio_total_shares'] = sum(item.shares for item in portfolio_items)
        context['portfolio_total_value'] = sum(item.shares * item.stock.current_price for item in portfolio_items)
        return context


    def __str__(self):
        """
            return the portfolio information
        """
        return f"{self.user}'s portfolio - {self.stock.ticker}"


class WatchList(models.Model):
    """
        Watchlist model to store user's watchlist information
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="watchlist")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    added_date = models.DateField(auto_now_add=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def __str__(self):
        """
            return the watchlist information
        """
        return f"{self.user}'s watchlist - {self.stock.ticker}"


class Transaction(models.Model):
    """
        Transaction model to store user's transaction information
    """
    TRANSACTION_CHOICES = [  # transaction available choices
        ('buy', 'Buy'),
        ('sell', 'Sell')
    ]
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="transactions")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_CHOICES)


    class Meta:
        """
            ordering the transaction by purchase date
        """
        ordering = ['-purchase_date'] 


    def __str__(self):
        """
            return the transaction information
        """
        return f"{self.user} {self.transaction_type} {self.stock.ticker} at ${self.purchase_price}"
