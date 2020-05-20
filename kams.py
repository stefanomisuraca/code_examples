"""REST operations for KAMS scans."""

from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes as permission_classes_decorator #noqa
from oauth2_provider.contrib.rest_framework import IsAuthenticatedOrTokenHasScope #noqa
from nsapi.models import KamsScan
from nsapi.serializers import KamsScanISerializer
import logging

logger = logging.getLogger('shapewatch')
# IsAuthenticatedOrTokenHasScope


class KamsView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin
):
    """Class handler, returns unique users."""

    required_scopes = ['read']
    serializer_class = KamsScanISerializer
    permission_classes = (IsAuthenticated, )
    swagger_schema = None

    def get_queryset(self):
        """Return custom queryset."""
        return KamsScan.objects.filter(
            user=self.request.user,
            status="complete"
        )

    def list(self, request):
        """Handle GET method."""
        user = request.user
        scans = KamsScan.objects.filter(
            user=user,
            status="complete"
        )
        serialized_scans = KamsScanISerializer(scans, many=True).data
        return Response({
            "data": serialized_scans
        })

    def retrieve(self, request, pk):
        """Retrieve method, details GET."""
        try:
            scan = KamsScan.objects.get(pk=pk, user=request.user)
        except KamsScan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serialized_scan = KamsScanISerializer(scan).data
        return Response(serialized_scan)
