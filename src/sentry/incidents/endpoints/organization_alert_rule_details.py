from __future__ import absolute_import

from rest_framework import status
from rest_framework.response import Response

from sentry.api.serializers import serialize
from sentry.api.serializers.models.alert_rule import DetailedAlertRuleSerializer
from sentry.incidents.endpoints.bases import OrganizationAlertRuleEndpoint
from sentry.incidents.endpoints.serializers import UnifiedAlertRuleSerializer as DrfAlertRuleSerializer
from sentry.incidents.logic import AlreadyDeletedError, delete_alert_rule


class OrganizationAlertRuleDetailsEndpoint(OrganizationAlertRuleEndpoint):
    def get(self, request, organization, alert_rule):
        """
        Fetch an alert rule.
        ``````````````````
        :auth: required
        """
        data = serialize(alert_rule, request.user, DetailedAlertRuleSerializer())
        return Response(data)

    def put(self, request, organization, alert_rule):
        print("Got put request!", alert_rule)
        print("Data:", request.data)
        serializer = DrfAlertRuleSerializer(
            context={"organization": organization, "access": request.access},
            instance=alert_rule,
            data=request.data,
            # partial=True,
        )

        if serializer.is_valid():
            alert_rule = serializer.save()
            return Response(serialize(alert_rule, request.user), status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, organization, alert_rule):
        try:
            # TODO: Ensure delete_alert_rule deletes triggers + actions as well.
            delete_alert_rule(alert_rule)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AlreadyDeletedError:
            return Response(
                "This rule has already been deleted", status=status.HTTP_400_BAD_REQUEST
            )
