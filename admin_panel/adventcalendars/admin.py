from django.contrib import admin

from .models import AdventClaim, AdventDayConfig


@admin.register(AdventDayConfig)
class AdventDayConfigAdmin(admin.ModelAdmin):
    list_display = ("day", "reward_type", "enabled", "ball", "special")
    list_filter = ("enabled", "reward_type")
    search_fields = ("description",)


@admin.register(AdventClaim)
class AdventClaimAdmin(admin.ModelAdmin):
    list_display = ("player", "day", "claimed_at")
    list_filter = ("day",)
    search_fields = ("player__discord_id",)
    autocomplete_fields = ("player",)
