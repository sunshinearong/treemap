"""Assignment 2: Trees for Treemap

=== CSC148 Fall 2016 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
import os
from random import randint
import math


class AbstractTree:
    """A tree that is compatible with the treemap visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you adding and implementing
    new public *methods* for this interface.

    === Public Attributes ===
    @type data_size: int
        The total size of all leaves of this tree.
    @type colour: (int, int, int)
        The RGB colour value of the root of this tree.
        Note: only the colours of leaves will influence what the user sees.

    === Private Attributes ===
    @type _root: obj | None
        The root value of this tree, or None if this tree is empty.
    @type _subtrees: list[AbstractTree]
        The subtrees of this tree.
    @type _parent_tree: AbstractTree | None
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - colour's elements are in the range 0-255.

    - If _root is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - _subtrees IS allowed to contain empty subtrees (this makes deletion
      a bit easier).

    - if _parent_tree is not empty, then self is in _parent_tree._subtrees
    """
    def __init__(self, root, subtrees, data_size=0):
        """Initialize a new AbstractTree.

        If <subtrees> is empty, <data_size> is used to initialize this tree's
        data_size. Otherwise, the <data_size> parameter is ignored, and this tree's
        data_size is computed from the data_sizes of the subtrees.

        If <subtrees> is not empty, <data_size> should not be specified.

        This method sets the _parent_tree attribute for each subtree to self.

        A random colour is chosen for this tree.

        Precondition: if <root> is None, then <subtrees> is empty.

        @type self: AbstractTree
        @type root: object
        @type subtrees: list[AbstractTree]
        @type data_size: int
        @rtype: None
        """
        r = randint(0,255)
        g = randint(0,255)
        b = randint(0,255)
        self.colour =(r,g,b)#initial colour
        self._root = root#initial root
        self._subtrees = subtrees#initial subtrees
        if self._subtrees == []:
            self.data_size = data_size#initial data size
        else:
            self.data_size = sum([subtree.data_size for subtree in self._subtrees])
        self._parent_tree = None
        for subtree in self._subtrees:
            subtree._parent_tree = self#initial parents of subtrees
       

    def is_empty(self):
        """Return True if this tree is empty.

        @type self: AbstractTree
        @rtype: bool
        """
        return self._root is None

    def generate_treemap(self, rect):
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]
        """
        if self._subtrees == []:#leaf
            return [(rect,self.colour)]
        else:
            rects = []
            move = 0
            for subtree in self._subtrees:
                rate = float(subtree.data_size)/self.data_size#the rate of subtree in its parent
                x,y,width,height = rect#unpack input rect
                if width > height:
                    x = x +move#update x
                    width = round(rate*width)#update width
                    rects.extend(subtree.generate_treemap((x,y,width,height)))#implement treemap algorithm
                    move += width#update move
                else:
                    y = y +move#update y
                    height = round(rate*height)#update height
                    rects.extend(subtree.generate_treemap((x,y,width,height)))#implement treemap algorithm
                    move += height#update move
            return rects
    

    def get_separator(self,pos,rect):
        """Return the string used to separate nodes in the string
        representation of a path from the tree root to a leaf.

        Used by the treemap visualiser to generate a string displaying
        the items from the root of the tree to the currently selected leaf.

        This should be overridden by each AbstractTree subclass, to customize
        how these items are separated for different data domains.

        @type self: AbstractTree
        @rtype: str
        """
        rects = self.generate_treemap(rect)#get size,place and colour of leaves
        selected_leaf_index = 0#which leaf you choose
        for rect in rects:
            if pos[0] >rect[0][0] and pos[1] >rect[0][1] and \
                pos[0]<rect[0][0]+rect[0][2] and pos[1]<rect[0][1]+rect[0][3] :#satisfy condition
                    index = 0
                    for subtree in self._subtrees:
                        for leaf in subtree._subtrees:#search the whole tree to find selected leaf
                            if index + 1 == selected_leaf_index:#find it
                                return ' '.join([self._root,subtree._root,leaf._root])#return leaf name
                            index += 1
            selected_leaf_index += 1
        raise NotImplementedError
    
    def change_leaf_size(self,selected_leaf,add_minus):
        for subtree in self._subtrees:
            for tree in subtree._subtrees:#search the whole tree
                if ' '.join([self._root,subtree._root,tree._root]) == selected_leaf:#find selected leaf
                    if add_minus == 1 or add_minus == 'add':#click is left or input is 'add' ,add data size
                        add = round(tree.data_size*0.4)
                        tree.data_size += add #add 40% percent of self size
                        tree._parent_tree.data_size += add#update parent size
                        tree._parent_tree._parent_tree.data_size += add#update grandparent size
                    if add_minus == 3 or add_minus == 'minus':
                        minus = round(tree.data_size*0.4)
                        tree.data_size -= minus#minus 40% percent of self size
                        tree._parent_tree.data_size -= minus#update parent size
                        tree._parent_tree._parent_tree.data_size -= minus#update grandparent size
        return self

class FileSystemTree(AbstractTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _root attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/David/csc148/assignments'

    The data_size attribute for regular files as simply the size of the file,
    as reported by os.path.getsize.
    """
    def __init__(self, path):
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        print(path)
        @type self: FileSystemTree
        @type path: str
        @rtype: None
        """
        r = randint(0,255)
        g = randint(0,255)
        b = randint(0,255)
        self.colour =(r,g,b)#initial colour
        if os.path.isdir(path) :#path is a directry,create subtree for each file in it 
            self._subtrees=[]
            self._root = path.split('\\')[-1]#filename
            self._parent_tree = None#initial parent
            for subpath in os.listdir(path):
                subtree = FileSystemTree(os.path.join(path,subpath))#build subtree
                subtree._parent_tree = self#initial subtree parent
                self._subtrees.append(subtree)# add subtree already build
            self.data_size = sum([subtree.data_size for subtree in self._subtrees])#add subtrees data size
            
        else:
            self._subtrees = []#leaf
            self._parent_tree = None
            self._root = path.split('\\')[-1]#filename
            self.data_size = os.path.getsize(path)#leaf size
    def generate_treemap(self, rect):
        """Run the treemap algorithm on this tree and return the rectangles.

        Each returned tuple contains a pygame rectangle and a colour:
        ((x, y, width, height), (r, g, b)).

        One tuple should be returned per non-empty leaf in this tree.

        @type self: AbstractTree
        @type rect: (int, int, int, int)
            Input is in the pygame format: (x, y, width, height)
        @rtype: list[((int, int, int, int), (int, int, int))]
        
        """
        if self._subtrees == []:#current tree is leaf,return the input value
            rects = [(rect,self.colour)]
            return rects
        else:
            rects = []
            move = 0#how long next subtree should move 
            for subtree in self._subtrees:
                rate = float(subtree.data_size)/self.data_size#the rate of subtree in its parent
                x,y,width,height = rect#unpack input rect
                if width > height:
                    x = x +move#update x
                    width = round(rate*width)#update width
                    rects.extend(subtree.generate_treemap((x,y,width,height)))#implement treemap algorithm
                    move += width#update move
                else:
                    y = y +move#update y
                    height = round(rate*height)#update height
                    rects.extend(subtree.generate_treemap((x,y,width,height)))#implement treemap algorithm
                    move += height#update move
            return rects
        
if __name__ == '__main__':
    
    import python_ta
    # Remember to change this to check_all when cleaning up your code.
    python_ta.check_errors(config='pylintrc.txt')
