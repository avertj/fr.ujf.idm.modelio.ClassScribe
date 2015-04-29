
def indent(something, level=0):
  return (level * '    ') + str(something)

def split_in_chunks(something, charlimit=80):
  ret = []
  idx = 0
  total = 0
  ret.insert(idx, '')
  for word in something.replace('\n', ' ').replace('\r', '').split(' '):
    if (len(word) + total) > charlimit:
      idx += 1
      ret.insert(idx, '')
      total = 0
    total += (len(word) + 1)
    ret[idx] += ' ' + word
  return ret


class SCNObject(object):

  def __init__(self, name):
    self.name = name
    self.summary = ''
    self.description = ''

  def setName(self, arg): self.name = arg

  def setSummary(self, arg): self.summary = arg

  def setDescription(self, arg): self.description = arg

  def generateComments(self, level=0):
    ret = ''
    if self.summary:
      ret += indent('S: ' + self.summary + '\n', level)
    if self.description:
      for line in split_in_chunks(self.description):
        ret += indent('D:' + line + '\n', level)
    return ret


class SCNEnumeration(SCNObject):

  def __init__(self, name):
    super(SCNEnumeration, self).__init__(name)
    self.litterals = []

  def addLitteral(self, litt):
    if litt not in self.litterals:
      self.litterals.append(litt)

  def removeLitteral(self, litt):
    self.litterals.remove(litt)

  def generate(self, level=0):
    ret = indent('e %s\n' % self.name, level)
    ret += super(SCNEnumeration, self).generateComments(level + 1)
    for litt in self.litterals:
      ret += litt.generate(level + 1) + '\n'
    return ret


class SCNEnumerationLitteral(SCNObject):

  def __init__(self, name):
    super(SCNEnumerationLitteral, self).__init__(name)

  def generate(self, level=0):
    ret = indent(self.name, level)
    ret += super(SCNEnumerationLitteral, self).generateComments(level + 1)
    return ret


class SCNClass(SCNObject):

  def __init__(self, name):
    super(SCNClass, self).__init__(name)
    self.attributes = []
    self.operations = []
    self.roles = []
    self.inhFrom = []

  def setAbstract(self, abstr):
    self.abstract = abstr

  def addAttribute(self, attr):
    self.attributes.append(attr)

  def addOperation(self, op):
    self.operations.append(op)

  def addRole(self, role):
    self.roles.append(role)

  def addParentClass(self, parent):
    self.inhFrom.append(parent)

  def generate(self, level=0):
    supcl = ''
    for p in self.inhFrom:
      supcl += p + ', '
    line = ('a ' if self.abstract else '') + self.name + (' < ' + supcl[:-2] if supcl else '')

    ret = indent(line + '\n', level)
    ret += super(SCNClass, self).generateComments(level + 1)
    for attr in self.attributes:
      ret += attr.generate(level + 1)
    for op in self.operations:
      ret += op.generate(level + 1)
    for role in self.roles:
      ret += role.generate(level + 1)
    return ret


class SCNAttribute(SCNObject):

  def __init__(self, name):
    super(SCNAttribute, self).__init__(name)
    self.visibility = ''
    self.typ = ''

  def setVisibility(self, vis):
    self.visibility = vis

  def setDerived(self, deriv):
    self.derived = deriv

  def setType(self, typ):
    self.typ = typ

  def setCardinality(self, card):
    self.cardinality = card

  def generate(self, level=0):
    line = ('/ ' if self.derived else '') + \
        ((self.visibility + ' ') if self.visibility else '') + self.name
    if self.typ:
      line += ' : ' + self.typ
      if self.cardinality:
        line += ' ' + self.cardinality.generate()
    ret = indent(line + '\n', level)
    ret += super(SCNAttribute, self).generateComments(level + 1)
    return ret


class SCNOperation(SCNObject):

  def __init__(self, name):
    super(SCNOperation, self).__init__(name)
    self.visibility = ''
    self.returnType = ''
    self.parameters = []

  def setAbstract(self, abstr):
    self.abstract = abstr

  def setVisibility(self, vis):
    self.visibility = vis

  def setReturnType(self, typ):
    self.returnType = typ

  def addParameter(self, param):
    self.parameters.append(param)

  def generate(self, level=0):
    line = ('a ' if self.abstract else '') + \
        ((self.visibility + ' ') if self.visibility else '') + self.name + '()'
    if self.returnType:
      line += ' : ' + self.returnType
    ret = indent(line + '\n', level)
    ret += super(SCNOperation, self).generateComments(level + 1)
    for p in self.parameters:
      ret += p.generate(level + 1)
    return ret


class SCNRole(SCNObject):

  def __init__(self, name):
    super(SCNRole, self).__init__(name)
    self.visibility = ''
    self.kind = ''
    self.typ = ''
    self.inv = None

  def setDerived(self, deriv):
    self.derived = deriv

  def setVisibility(self, vis):
    self.visibility = vis

  def setKind(self, kind):
    self.kind = kind

  def setCardinality(self, card):
    self.cardinality = card

  def setType(self, typ):
    self.typ = typ

  def setInverse(self, inv):
    self.inv = inv

  def generate(self, level=0):
    line = ('/ ' if self.derived else '') + \
        ((self.visibility + ' ') if self.visibility else '')
    line += ((self.kind + ' ') if self.kind else '') + self.name
    line += ' : ' + self.typ
    if self.cardinality:
      line += ' ' + self.cardinality.generate()
    if self.inv:
      line += ' inv ' + self.inv.name
      line += ' ' + self.inv.cardinality.generate()
    ret = indent(line + '\n', level)
    ret += super(SCNRole, self).generateComments(level + 1)
    return ret


class SCNParameter(SCNObject):

  def __init__(self, name):
    super(SCNParameter, self).__init__(name)
    self.typ = ''

  def setType(self, typ):
    self.typ = typ

  def generate(self, level=0):
    line = self.name + (' : ' + self.typ if self.typ else '')
    ret = indent(line + '\n', level)
    ret += super(SCNParameter, self).generateComments(level + 1)
    return ret


class SCNCardinality(object):

  def __init__(self, mini, maxi):
    self.mini = str(mini)
    self.maxi = str(maxi)

  def setMin(self, mini):
    self.mini = mini

  def setMax(self, maxi):
    self.maxi = maxi

  def generate(self):
    card = ''
    if self.maxi == self.mini and self.maxi != '1':
      card = '[%s]' % self.maxi
    elif self.maxi == self.mini and self.maxi == '1':
			return card
    elif self.mini == '0' and self.maxi == '*':
      card = '[*]'
    else:
      card = '[%s..%s]' % (self.mini, self.maxi)
    return card


classes = []
enums = []

def add_comments(elem, descriptor):
  for desc in descriptor:
    if desc.getModel().getName() == 'summary':
      elem.setSummary(desc.getContent())
    elif desc.getModel().getName() == 'description':
      elem.setDescription(desc.getContent())

def create_type(typ):
  """
  Generate USE OCL basic type. Note that
  type conversions are required.
  """
  if typ in ('integer', 'long', 'short'):
    return 'integer'
  if typ in ('float', 'double'):
    return 'float'
  if typ in ('string', 'char'):
    return 'string'
  return typ

def create_enum(enum):
  scnenum = SCNEnumeration(enum.getName())

  add_comments(scnenum, enum.getDescriptor())

  for lit in enum.getValue():
    scnlit = SCNEnumerationLitteral(lit.getName())
    add_comments(scnlit, lit.getDescriptor())
    scnenum.addLitteral(scnlit)
  return scnenum


def create_class(cla):
  scnclass = SCNClass(cla.getName())

  add_comments(scnclass, cla.getDescriptor())

  scnclass.setAbstract(cla.isIsAbstract())

  for p in cla.getParent():
    scnclass.addParentClass(p.getSuperType().getName())
  for att in cla.getOwnedAttribute():
    scnclass.addAttribute(create_attribute(att))
  for op in cla.getOwnedOperation():
    scnclass.addOperation(create_operation(op))
  for role in cla.getOwnedEnd():
    scnclass.addRole(create_role(role))
  return scnclass


visi = {VisibilityMode.PUBLIC: '+', VisibilityMode.PRIVATE: '-', VisibilityMode.PROTECTED: '#', VisibilityMode.PACKAGEVISIBILITY: '~'}
rkind = {AggregationKind.KINDISCOMPOSITION: '<#>', AggregationKind.KINDISAGGREGATION: '<>'}

def create_operation(op):
  scnopr = SCNOperation(op.getName())

  add_comments(scnopr, op.getDescriptor())

  scnopr.setAbstract(op.isIsAbstract())
  if op.getReturn():
    scnopr.setReturnType(create_type(op.getReturn().getType().getName()))
  try:
    scnopr.setVisibility(visi[op.getVisibility()])
  except:
    pass
  for p in op.getIO():
    param = SCNParameter(p.getName())
    add_comments(param, p.getDescriptor())
    param.setType(create_type(p.getType().getName()))
    scnopr.addParameter(param)
  return scnopr

def create_attribute(att):
  scnattr = SCNAttribute(att.getName())

  add_comments(scnattr, att.getDescriptor())

  scnattr.setDerived(att.isIsDerived())
  try:
    scnattr.setVisibility(visi[att.getVisibility()])
  except:
    pass
  scnattr.setCardinality(SCNCardinality(att.getMultiplicityMin(), (att.getMultiplicityMax())))
  scnattr.setType(create_type(att.getType().getName()))
  return scnattr

def create_role(role):
  if role.getName():
    scnrole = SCNRole(role.getName())
  else:
    scnrole = SCNRole('unnamed')

  add_comments(scnrole, role.getDescriptor())

  scnrole.setDerived(role.isIsDerived())
  try:
    scnrole.setVisibility(visi[role.getVisibility()])
  except:
    pass
  try:
    scnrole.setKind(rkind[role.getAggregation()])
  except:
    pass
  scnrole.setCardinality(SCNCardinality(role.getMultiplicityMin(), (role.getMultiplicityMax())))
  scnrole.setType(role.getOpposite().getOwner().getName())
  if role.getOpposite().getName():
    inv = SCNRole(role.getOpposite().getName())
    inv.setCardinality(SCNCardinality(role.getOpposite().getMultiplicityMin(), (role.getOpposite().getMultiplicityMax())))
    scnrole.setInverse(inv)
  return scnrole

def parse_package(pkg):
  for elem in pkg.ownedElement:
    if isinstance(elem, Package):
      pass
    if isinstance(elem, Enumeration):
      enums.append(create_enum(elem))
    if isinstance(elem, Class):
      classes.append(create_class(elem))

if len(selectedElements) == 1:
  elem=selectedElements[0]
# for elem in selectedElements:
if isinstance(elem, Package):
  parse_package(elem)

for e in enums:
  print e.generate()
for c in classes:
  print c.generate()
