Description of Gaphors data model
=================================

Gaphor is an UML tool. In order to keep as close as possible to the UML
specification the data model is based on the UML Metamodel. Since the OMG has
an XMI (XML) specification of the metamodel, the easiest way to do that is to
generate the code directly from the model. Doing this raises two issues:

   1. There are more attributes defined in the data model than we will use.
   2. How do we check if the model is consistent?

The first point is not such a problem: attributes we don't use don't consume memory.

There are no consistency rules in the XML definition, we have to get them from
the UML syntax description. It is probably best to create a special consistency
module that checks the model and reports errors.

In the UML metamodel all classes are derived from :ref:`Element <uml_element>`. So all we have
to do is create a substitute for :ref:`Element <uml_element>` that gives some behaviour to the
data objects.

The data model is described in Python. Since the Python language doesn't make
a difference between classes and objects, we can define the possible
attributes that an object of a particular kind can have in a dictionary
(name-value map) at class level. If a value is set, the object checks if an
attribute exists in the class' dictionary (and the parents dictionary). If it
does, the value is assigned, if it doesn't an exception is raised.

Bidirectional references
------------------------

But how, you might wonder, do you handle bidirectional references (object one
references object two and vice versa)? Well, this is basically the same as the
uni-directional reference. Only now we need to add some extra information to
the dictionary at class level. We just define an extra field that gives us
the name of the opposite reference and voila, we can create bi-directional
references. You should check out the code in ``gaphor/UML/element.py`` for more details.

Implementation
--------------

This will allow the user to assign a value to an instance of ``Element`` with
name ``name``. If no value is assigned before the value is requested, it 
returns and empty string ''::

  m = Class()
  print(m.name)              # Returns ''
  m.name = 'MyName'
  print(m.name)	             # Returns 'MyName'
   
  m = Element()
  c = Comment()
  print(m.comment)             # Returns an empty list '[]'
  print(c.annotatedElement)    # Returns an empty list '[]'
  m.comment = c                # Add 'c' to 'm.comment' and add 'm' to 'c.annotatedElement'
  print(m.comment)             # Returns a list '[c]'
  print(c.annotatedElement)    # Returns a list '[m]'

All this wisdom is defined in the data-models base class: ``Element``. 
The datamodel itself code is generated. 

Extensions to the data model
----------------------------

A few changes have been made to Gaphor's implementation of the metamodel. First
of all some relationships have to be modified since the same name is used for
different relationships. Some n:m relationships have been made 1:n. These are
all small changes and should not restrict the usability of Gaphor's model.

The biggest change is the addition of a whole new class: Diagram. Diagram is
inherited from Namespace and is used to hold a diagram. It contains a
``gaphas.canvas.Canvas`` object which can be displayed on screen by a
``DiagramView`` class.

.. _uml_element:

UML.Element
-----------
.. autoclass:: gaphor.UML.element.Element
   :members:

