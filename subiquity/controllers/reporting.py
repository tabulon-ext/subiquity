# Copyright 2019 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import copy
import logging

from curtin.reporter import (
    available_handlers,
    update_configuration,
    )
from curtin.reporter.events import (
    report_finish_event,
    report_start_event,
    status,
    )
from curtin.reporter.handlers import (
    LogHandler,
    )

from subiquity.controller import NoUIController


class LogHandler(LogHandler):
    def publish_event(self, event):
        level = getattr(logging, event.level)
        logger = logging.getLogger('')
        logger.log(level, event.as_string())


available_handlers.unregister_item('log')
available_handlers.register_item('log', LogHandler)

INITIAL_CONFIG = {'logging': {'type': 'log'}}
NON_INTERACTIVE_CONFIG = {'builtin': {'type': 'print'}}


class ReportingController(NoUIController):

    autoinstall_key = "reporting"

    def __init__(self, app):
        self.config = copy.deepcopy(INITIAL_CONFIG)
        super().__init__(app)

    def load_autoinstall_data(self, data):
        if self.app.interactive():
            return
        self.config.update(copy.deepcopy(NON_INTERACTIVE_CONFIG))
        if data is not None:
            self.config.update(copy.deepcopy(data))

    def start(self):
        update_configuration(self.config)

    def report_start_event(self, name, description, level):
        report_start_event(name, description, level=level)

    def report_finish_event(self, name, description, result, level):
        result = getattr(status, result.name, status.WARN)
        report_finish_event(name, description, result, level=level)
