from search_views.filters import BaseFilter


class PlayerDeclarationFilter(BaseFilter):
    search_fields = {
        "search_text": ["player__name", "elected_country__name"],
        "search_year": {"operator": "__year", "fields": ["player__date_of_birth"]},
    }
