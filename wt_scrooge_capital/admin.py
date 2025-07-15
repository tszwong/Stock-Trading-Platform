# By: Tsz Kit Wong
# File: wt_scrooge_capital/admin.py

from django.contrib import admin
from .models import Portfolio, StockPriceHistory, Transaction, UserProfile, Stock, WatchList

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Stock)
admin.site.register(StockPriceHistory)
admin.site.register(Portfolio)
admin.site.register(WatchList)
admin.site.register(Transaction)