
def select_scn_file():
    from org.eclipse.swt.widgets import FileDialog, Shell
    from org.eclipse.swt import SWT

    display = Display.getDefault().getActiveShell()
    shell = Shell(display)

    fd = FileDialog(shell, SWT.OPEN)
    fd.setText('Open')
    filterExt = ['*.scn', '*.*']
    fd.setFilterExtensions(filterExt)
    return fd.open()

def import_tree(scn_file, pkg):
    t = TextualTreeReader(scn_file).getTextualTree()
    #print len(tree.getChildren())
    for c in t.getChildren():
        name = c.getHeadline()
        if name.split()[0] in ['e', 'enum']:
            create_enum(c, pkg)
        else:
            create_class(c, pkg)

def add_comments(elem, children):
    description = ''
    summary = ''
    for c in children:
        if c.getHeadline()[:3] is 'D: ':
            description += c.getHeadline()[3:] + '\n'
        elif c.getHeadline()[:3] is 'S: ':
            summary += c.getHeadline()[3:] + '\n'
    # i dont know what the first parameter is supposed to be
    # https://www.modelio.org/documentation/javadoc-3.1/org/modelio/metamodel/uml/infrastructure/ModelElement.html#putNoteContent(java.lang.String, java.lang.String, java.lang.String)
    if summary: elem.putNoteContent('org.modelio.module.modelermodule.impl.ModelerModuleModule', 'summary', summary)
    if description: elem.putNoteContent('org.modelio.module.modelermodule.impl.ModelerModuleModule', 'description', description)

def ignore_line(line):
    return line.split()[0] in ['D:', 'S:', 'd:', 's:']

def create_class(node, pkg):
    trans = modelingSession.createTransaction("Class creation") 
    try:
        name = node.getHeadline()
        model = modelingSession.getModel()
        abstract = False
        if name.split()[0] in ['a', 'abstract']:
            abstract = True
        if abstract:
            cla = model.createClass(name.split()[1], pkg)
            cla.setIsAbstract(abstract)
        else:
            cla = model.createClass(name.split()[0], pkg)

        add_comments(cla, node.getChildren())

        for c in node.getChildren():
            if not ignore_line(c.getHeadline()):
                pass
        trans.commit()
    except:
        trans.rollback()
        raise

def create_enum(node, pkg):
    trans = modelingSession.createTransaction("Enum creation") 
    try:
        name = node.getHeadline()
        model = modelingSession.getModel()
        enum = model.createEnumeration(name.split()[1], pkg)

        add_comments(enum, node.getChildren())

        for c in node.getChildren():
            if not ignore_line(c.getHeadline()):
                lit = model.createEnumerationLiteral(c.getHeadline(), enum)
        trans.commit()
    except:
        trans.rollback()
        raise

if len(selectedElements) == 1:
    elem=selectedElements[0]

    if not isinstance(elem, Package):
        print 'Please select a package first, aborting.'
    else :
        scn_file = select_scn_file()
        if scn_file:
            import_tree(scn_file, elem)
        else:
            print 'No file selected, aborting.'
else:
    print 'Please select only one package, aborting.'

#----------------------------------------------------------------------------
# textual_tree
#----------------------------------------------------------------------------
# Support for reading trees represented as nested lines.
#
# Licence: LGPL
# Author: jmfavre
#
# History
#   Version 1.0 - March 22, 2014
#      - first version. Line numbering not implemented yet.
#

#--- Tree ---
# Simple tree structure where each node has the following elements:
#    - "headline" : a (possibly multiline) string corresponding to
#                     the main content of the node.
#    - "children" : a list of subtrees. This list is empty for leaves.
#    - "parent"   : the parent of a node or None for the root.
# Note that the subclass TextualTree possess additional elements
class Tree(object):
 #-- main interface

    def getHeadline(self): return self.headline

    def getChildren(self): return self.children

    def getParent(self): return self.parent

    def hasChildren(self): return len(self.children) > 0

    def getLastChild(self): return self.children[len(self.children) - 1]

    def getLastNode(self):
        if self.hasChildren():
            return self.getLastChild().getLastNode()
        else:
            return self
    #-- update interface

    def addChild(self, tree):
        self.children = self.children + [tree]

    def __init__(self, headline=None, children=[], parent=None):
        self.headline = headline
        self.children = children
        self.parent = parent
        for child in children:
            child.parent = self

#--- TextualTree ---
# This class enables to deal textual representation of trees.
# Additionnaly to the "Tree" structure the following elements
# are added on each node:
#    - "indent" : a integer value corresponding to the indentation
#    - "comment" : a potentially multiline string corresponding to
#                  the comments appearing before the node


class TextualTree(Tree):
    #-- main interface

    def getIndent(self): return self.indent

    def getComment(self): return self.comment

    def getLineNumber(self): return self.lineNumber

    # update interface
    def __init__(self, lineNumber=None, indent=None, comment=None, headline=None, children=[], parent=None):
        Tree.__init__(self, headline, children, parent)
        self.indent = indent
        self.comment = comment
        self.lineNumber = lineNumber

    def setLineNumber(self, lineNum): self.lineNumber = lineNum

    def setIndent(self, indent): self.indent = indent

    def setComment(self, comment): self.comment = comment

    def searchTree(self, indent):
        """ Search for the last tree matching this indent
        """
        if self.indent == indent:
            return self
        elif self.hasChildren():
            return self.getLastChild().searchTree(indent)
        else:
            return None

    def addLine(self, lineNumber, indent, comment, headline):
        # print "addLine("+str(indent)+headline+")"
        lastNode = self.getLastNode()
        # print "indent is ",indent
        if indent == lastNode.getIndent():
            # same level as the last node
            parent = lastNode.getParent()
            # print "  same level as "+("root" if parent.headline is None else
            # parent.headline)
        elif indent > lastNode.getIndent():
            # this is a new nesting
            parent = lastNode
            # print "  nested level in "+("root" if parent.headline is None else
            # parent.headline)
        else:
            # search in previous open nestings
            sameLevelNode = self.searchTree(indent)
            if sameLevelNode is None:
                print "***error*** cannot find node with nesting " + str(indent)
            parent = sameLevelNode.getParent()
            # print "  previous nesting, added in "+("root" if parent.headline is None
            # else parent.headline)
        node = TextualTree(lineNumber, indent, comment, headline, [], parent)
        parent.children += [node]

    def text(self):
        if self.headline is None or self.indent is None:
            out = ""
        else:
            if self.comment is None or self.comment == "":
                out = ""
            else:
                self.comment + "\n"
            out += (" " * self.indent) + self.headline + "\n"
        for child in self.children:
            out += child.text()
        return out

    def toList(self):
        if self.headline is None or self.indent is None:
            out = ""
        else:
            out = self.headline
        for child in self.children:
            out += "(" + child.toList() + " )"
        return out


class TextualTreeReader(object):

    def __init__(self, linesOrFilename):
        """ Create the tree from a file or a list of lines.
        """
        if isinstance(linesOrFilename, basestring):
            lines = [line.strip("\n") for line in open(linesOrFilename)]
        else:
            lines = linesOrFilename
        self.rawLines = lines
        self.structuredLines = None

    def _getStructuredLines(self):
        import re
        if self.structuredLines is not None:
            return self.structuredLines
        else:
            self.structuredLines = []
            commentRE = r"^ *(--.*)?$"
            indentedRE = r"^( *)(.*)$"
            continuationRE = r"^ *: ?(.*)$"
            index = 0
            comment = ""
            headline = None
            indentString = None
            for rawLine in self.rawLines:
                matchComment = re.match(commentRE, rawLine)
                if matchComment:
                #-- This is a comment line
                    if headline is not None:
                    # the previous headline is now finished
                        self._addLine(comment, indentString, headline)
                        headline = None
                        comment = ""
                    # In all cases add the comment line to the comment
                    comment += ("" if comment == "" else "\n") + matchComment.group()
                else:
                    matchContinuation = re.match(continuationRE, rawLine)
                    if matchContinuation:
                    #-- This is a continuation line
                        if headline is not None:
                        # Add the continuation to the headline
                            headline += "\n" + matchContinuation.group(1)
                        else:
                        # Ignore the continuation
                            pass
                    else:
                        matchIndentedLine = re.match(indentedRE, rawLine)
                        # There is always a match given the pattern
                        #-- this is neither a comment, nor a continuation, hence a headline
                        if headline is not None:
                        # After a headline. Push this one to the list.
                            self._addLine(comment, indentString, headline)
                            comment = ""
                        indentString = matchIndentedLine.group(1)
                        headline = matchIndentedLine.group(2)
            if headline is not None:
                self._addLine(comment, indentString, headline)
            return self.structuredLines

    def _addLine(self, comment, indentString, headline):
        self.structuredLines += [(comment, len(indentString), headline)]

    def getTextualTree(self):
        tree = TextualTree(-1, -1)
        lines = self._getStructuredLines()
        for (comment, indent, headline) in lines:
            tree.addLine(-1, indent, comment, headline)
        return tree
