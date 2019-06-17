from collective.contentrules.movetofield import MoveToFieldMessageFactory as _
from zope import schema
from zope.interface import Interface
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from plone.app.vocabularies.catalog import CatalogSource
from Products.CMFCore.interfaces import IFolderish


class IMoveAction(Interface):

    destination = RelationChoice(
        title=_(u"Destination"),
        vocabulary='plone.app.vocabularies.Catalog',
        required=True,
    )

    bypasspermissions = schema.Bool(
        title=_(u"Bypass User Permissions"),
        description=_(u"When selected, permissions will be bypassed and the "
                      u"object will be moved regardless of whether or not the"
                      u"user has permission to move it."),
        default=False,
        required=False
    )

    reindex = schema.Bool(
        title=_(u"Reindex object after moving it"),
        default=False,
        required=False
    )
