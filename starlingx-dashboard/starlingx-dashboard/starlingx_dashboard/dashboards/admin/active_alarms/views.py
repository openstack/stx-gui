# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# Copyright (c) 2013-2019 Wind River Systems, Inc.
#


import logging

from django.utils.translation import ugettext_lazy as _  # noqa
from django.views.generic import TemplateView

from horizon import exceptions
from openstack_dashboard.api.base import is_service_enabled
from starlingx_dashboard.api import dc_manager
from starlingx_dashboard.api import fm


LOG = logging.getLogger(__name__)


class BannerView(TemplateView):
    template_name = 'header/_alarm_banner.html'

    def get_context_data(self, **kwargs):

        context = super(BannerView, self).get_context_data(**kwargs)

        if not self.request.is_ajax():
            raise exceptions.NotFound()

        if (not self.request.user.is_authenticated() or
                not self.request.user.is_superuser):
            context["alarmbanner"] = False
        elif 'dc_admin' in self.request.META.get('HTTP_REFERER'):
            summaries = self.get_subcloud_data()
            central_summary = self.get_data()
            summaries.append(central_summary)
            context["dc_admin"] = True
            context["alarmbanner"] = True
            context["OK"] = len(
                [s for s in summaries if s.status == 'OK'])
            context["degraded"] = len(
                [s for s in summaries if s.status == 'degraded'])
            context["critical"] = len(
                [s for s in summaries if s.status == 'critical'])
            context["disabled"] = len(
                [s for s in summaries if s.status == 'disabled'])
        elif is_service_enabled(self.request, 'platform'):
            context["summary"] = self.get_data()
            context["alarmbanner"] = True

        return context

    def get_data(self):
        summary = None
        try:
            summary = fm.alarm_summary_get(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve alarm summary.'))

        return summary

    def get_subcloud_data(self):
        return dc_manager.alarm_summary_list(self.request)
