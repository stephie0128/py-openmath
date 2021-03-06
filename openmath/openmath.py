""" Contains a Data-structure for OpenMath and related objects. """
from collections import namedtuple as nt
from six.moves import zip_longest
from six import add_metaclass

class _OMMeta(type):
    """ Metaclass to simulate a struct type """
    def __new__(mcls, name, bases, props):
        if '_fields' not in props:
            fields = []
            for b in bases:
                for f in b._fields:
                    if f not in fields:
                        fields.append(f)
            props['_fields'] = fields
        return super(_OMMeta, mcls).__new__(mcls, name, bases, props)

    def __call__(cls, *args, **kwds):
        if len(args) > len(cls._fields):
            raise TypeError("%s() got too many positional arguments" % cls.__name__)
        values = {}
        for f, v in zip_longest(cls._fields, args):
            if v is None:
                v = kwds.get(f)
            elif f in kwds:
                raise TypeError("%s() got multiple values for argument '%s'" % (cls.__name__, f))

            if v is None:
                if hasattr(cls, '_default_' + f):
                    v = getattr(cls, '_default_' + f)
                else:
                    raise TypeError("%s() missing required argument '%s'" % (cls.__name__, f))
            elif hasattr(cls, '_clean_' + f):
                v = getattr(cls, '_clean_' + f)(v)

            values[f] = v
        return type.__call__(cls, **values)
        
    
@add_metaclass(_OMMeta)
class OMAny(object):
    """ Class for all OpenMath related objects. """
    _fields = []

    def __init__(self, **kwds):
        self._attrs = nt(self.__class__.__name__, self._fields)(**kwds)

    def __getattr__(self, name):
        return getattr(self._attrs, name)

    def __repr__(self):
        return repr(self._attrs)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self._attrs == other._attrs

class CDBaseAttribute(OMAny):
    """ Mixin for OpenMath Objects with a cdbase attribute. """
    _fields = ['cdbase']

    @staticmethod
    def _clean_cdbase(val):
        return str(val)
    _default_cdbase = None

class CommonAttributes(OMAny):
    """ Mixin for OpenMath Objects with common attributes. """
    _fields = ['id']

    @staticmethod
    def _clean_id(val):
        return str(val)
    _default_id = None
    
class CompoundAttributes(CommonAttributes, CDBaseAttribute):
    """ Mixin for OpenMath objects with compound attributes. """

    pass

class OMAnyVal(OMAny):
    """ Shared Class for OpenMath Expressions + OpenMath Derived Objects. """

    pass


class OMObject(OMAnyVal, CompoundAttributes):
    """ Represents a single OpenMath object. """
    _fields = ['omel', 'version', 'id', 'cdbase']

    @staticmethod
    def _clean_version(val):
        return str(val)
    _default_version = '2.0'

class OMExpression(OMAnyVal):
    """ Base class for all OpenMath Expressions (i.e. proper objects
    according to the specification). """

    pass


class OMReference(OMExpression, CommonAttributes):
    """ An OpenMath reference. """
    _fields = ['href', 'id']

    @staticmethod
    def _clean_href(val):
        # TODO: Think about using URI class here
        return str(val)


class OMBasicElement(OMAny):
    """ Basic OpenMath objects (section 2.1.1). """
    pass


class OMInteger(OMBasicElement, CommonAttributes):
    """ An OpenMath integer. """
    _fields = ['integer', 'id']

    @staticmethod
    def _clean_integer(val):
        try:
            return int(val)
        except TypeError:
            raise "%s() received malformed value '%r' for 'integer'" % (val, self.__class__.__name__)


class OMFloat(OMBasicElement, CommonAttributes):
    """ An OpenMath double. """
    _fields = ['double', 'id']

    @staticmethod
    def _clean_double(val):
        try:
            return float(val)
        except TypeError:
            raise "%s() received malformed value '%r' for 'double'" % (val, self.__class__.__name__)


class OMString(OMBasicElement, CommonAttributes):
    """ An OpenMath string. """
    _fields = ['string', 'id']

    _default_string = None
    
class OMBytes(OMBasicElement, CommonAttributes):
    """ An OpenMath list of bytes. """
    _fields = ['bytes', 'id']

class OMSymbol(OMBasicElement, CommonAttributes, CDBaseAttribute):
    """ An OpenMath symbol. """
    _fields = ['name', 'cd', 'id', 'cdbase']
    
    @staticmethod
    def _clean_name(val):
        # TODO: Verify if they match the regular expression?
        return str(val)

    @staticmethod
    def _clean_cd(val):
        # TODO: Verify if they match the regular expression?
        return str(val)


class OMVariable(OMBasicElement, CommonAttributes):
    """ An OpenMath variable. """
    _fields = ['name', 'id']
    
    @staticmethod
    def _clean_name(val):
        # TODO: Check if we match the regex here?
        return str(val)


class OMDerivedElement(OMAnyVal):
    """ Derived OpenMath objects (section 2.1.2). """

    pass


class OMForeign(OMDerivedElement, CompoundAttributes):
    """ An OpenMath Foreign Object. """
    _fields = ['obj', 'encoding', 'id', 'cdbase']

    @staticmethod
    def _clean_encoding(val):
        return str(val)
    _default_encoding = None

class OMCompoundElement(OMExpression):
    """ Compound OpenMath objects (section 2.1.3). """
    pass


class OMApplication(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Application Object. """
    _fields = ['elem', 'arguments', 'id', 'cdbase']
    
    @staticmethod
    def _clean_arguments(val):
        return list(val)


class OMAttribution(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Attribution Object. """
    _fields = ['pairs', 'obj', 'id', 'cdbase']
    

class OMAttributionPairs(CompoundAttributes):
    """ List of Attribution pairs. """
    _fields = ['pairs', 'id', 'cdbase']

    @staticmethod
    def _clean_pairs(val):
        return list(val)


class OMBinding(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Binding. """
    _fields = ['binder', 'vars', 'obj', 'id', 'cdbase']


class OMAttVar(CommonAttributes):
    """ Represents an attributed variable. """
    _fields = ['pairs', 'obj', 'id']


class OMBindVariables(CommonAttributes):
    """ List of OpenMath bound variables. """
    _fields = ['vars', 'id']
        
    @staticmethod
    def _clean_vars(val):
        return list(val)


class OMError(OMCompoundElement, CompoundAttributes):
    """ An OpenMath Error. """
    _fields = ['name', 'params', 'id', 'cdbase']
    
    @staticmethod
    def _clean_params(val):
        return list(val)


__all__ = ["OMAny", "CDBaseAttribute", "CommonAttributes",
           "CompoundAttributes", "OMAnyVal", "OMObject", "OMExpression",
           "OMReference", "OMBasicElement", "OMInteger", "OMFloat", "OMString",
           "OMBytes", "OMSymbol", "OMVariable", "OMDerivedElement",
           "OMForeign", "OMCompoundElement", "OMApplication", "OMAttribution",
           "OMAttributionPairs", "OMBinding", "OMAttVar",
           "OMBindVariables", "OMError"]
