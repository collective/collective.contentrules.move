# -*- coding:utf-8 -*-
from logging import getLogger

from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser
from OFS.SimpleItem import SimpleItem
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage
from collective.contentrules.move import MoveMessageFactory as _
from collective.contentrules.move.interfaces import IMoveAction
from plone import api
from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm
from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from zope.component import adapts
from zope.formlib import form
from zope.interface import Interface
from zope.interface import implements

logger = getLogger('collective.contentrules.move')


class MoveAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(IMoveAction, IRuleElementData)

    destination = ''
    bypasspermissions = False
    element = "collective.contentrules.move.ApplyMove"

    @property
    def summary(self):
        return _(u"Move content to ${destination}",
                 mapping=dict(field=self.destination))


class MoveActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IMoveAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.request = getattr(self.context, 'REQUEST', None)
        self.event = event

    def __call__(self):
        obj = self.event.object

        destination = getattr(self.element, 'destination')
        if destination is None:
            self.error("No destination defined in content rule.")
            return False
        destination = uuidToObject(IUUID(destination))
        bypasspermissions = getattr(self.element, 'bypasspermissions', False)

        sm = getSecurityManager()
        portal = api.portal.get()
        try:
            try:
                if bypasspermissions is True:
                    tmp_user = UnrestrictedUser(sm.getUser().getId(),
                                                '',
                                                ['Copy or Move'],
                                                '')
                    tmp_user = tmp_user.__of__(portal.acl_users)
                    newSecurityManager(self.request, tmp_user)
                    api.content.move(source=obj, target=destination)
            except Exception as e:
                # TODO: Handle exceptions more elegantly
                self.error(obj, e)
                return False
        finally:
            if bypasspermissions is True:
                setSecurityManager(sm)

        if getattr(self.element, 'reindex', False) is True:
            destination.reindexObject()

        return True

    def error(self, obj, error):

        title = utils.pretty_title_or_id(obj, obj)
        message = _(u"Unable to apply local roles on %s: %s" % (title, error))
        logger.error(message)
        if self.request is not None:
            IStatusMessage(self.request).addStatusMessage(message, type="error")


class MoveAddForm(AddForm):
    """An add form for local roles action.
    """
    form_fields = form.FormFields(IMoveAction)
    label = _(u"Add a Move Action")
    description = _(u"An action that moves content to a folder")
    schema = IMoveAction

    def create(self, data):
        a = MoveAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class MoveEditForm(EditForm):
    """An edit form for move action.
    """
    form_fields = form.FormFields(IMoveAction)
    label = _(u"Edit a Move Action")
    description = _(u"An action that moves content to a folder")
    schema = IMoveAction
