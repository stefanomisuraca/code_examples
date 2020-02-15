"""REST operations for personal trainers portal."""

import logging
from django.http import HttpResponse, JsonResponse
from nsapi.models import Scan
from oauth2_provider.views.generic import (
    ProtectedResourceView,
    ScopedProtectedResourceView
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from nsapi.util.common_functions import (
    get_personal_trainer_list,
    link_pt_to_user,
    unlink_user_from_pt
)
import json


logger = logging.getLogger('shapewatch')


class PersonalTrainers(ScopedProtectedResourceView, ProtectedResourceView):
    """Personal trainers operations."""

    required_scopes = ['read', 'write']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """Dispatch method."""
        return super(PersonalTrainers, self).dispatch(request, *args, **kwargs) #noqa

    def get(self, request):
        """Get a list of personal trainers."""
        user = request.user
        kiosks = Scan.objects.filter(
            user=user,
            kiosk_serial__isnull=False
        ).values("kiosk_serial").distinct()
        if not kiosks:
            return HttpResponse("No kiosks found", status=204)
        personal_trainers = get_personal_trainer_list(
            [kiosk.get('kiosk_serial') for kiosk in kiosks],
            user.username
        )
        return JsonResponse(personal_trainers, safe=False)

    def post(self, request):
        """Create a relation betweeen user and personal trainer."""
        user = request.user
        body = json.loads(request.body)
        personal_trainer = body.get('pt_id')
        response = link_pt_to_user(personal_trainer, user.username)
        return JsonResponse(response)

    def delete(self, request):
        """Delete the relation between user and personal trainer."""
        user = request.user
        body = json.loads(request.body)
        personal_trainer = body.get('pt_id')
        response = unlink_user_from_pt(personal_trainer, user.username)
        if response:
            return HttpResponse(status=204)
        else:
            return JsonResponse(
                {"error": "could not delete relation"},
                status=500
            )
