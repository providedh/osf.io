# -*- coding: utf-8 -*-
import httplib as http
import logging

from framework.auth.decorators import collect_auth
from framework.exceptions import HTTPError
from osf.models import (
    Guid,
    BaseFileNode,
)
from website.profile.utils import get_profile_image_url
from website.project.decorators import (
    must_have_permission,
    must_not_be_registration,
    must_be_valid_project,
    must_have_read_permission_or_be_public)
from website.project.views.node import _view_project

logger = logging.getLogger(__name__)