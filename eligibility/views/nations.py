from django.template.response import TemplateResponse
from guardian.shortcuts import get_objects_for_user


def declaration_list(request):
    qs = get_objects_for_user(
        request.user, "eligibility.view_playerdeclaration", with_superuser=False
    )
    object_list = qs.exclude(supersceded_by__isnull=False)
    context = {
        "object_list": object_list,
    }
    return TemplateResponse(request, "eligibility/playerdeclaration_list.html", context)
