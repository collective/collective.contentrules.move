from zope.i18nmessageid import MessageFactory


MoveMessageFactory = \
    MessageFactory('collective.contentrules.move')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
