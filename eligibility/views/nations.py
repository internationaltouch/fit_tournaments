from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from guardian.shortcuts import get_objects_for_user


@login_required
def declaration_list(request):
    if not request.user.groups.exists():
        return TemplateResponse(
            request, "eligibility/playerdeclaration_list_403.html", status=403
        )
    qs = get_objects_for_user(
        request.user,
        "eligibility.view_playerdeclaration",
        use_groups=True,
        any_perm=True,
    )
    object_list = qs.exclude(supersceded_by__isnull=False)
    context = {
        "object_list": object_list,
    }
    return TemplateResponse(request, "eligibility/playerdeclaration_list.html", context)
