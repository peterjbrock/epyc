#!/usr/bin/env python3

import html
import re

def sanitise(string):
	return html.escape(string)

class ParseError(Exception):
	pass

# Node Classes
# Used in the parsing and evaluation to define the syntax tree.
class Node:
	"Node meta-class."
	def __init__(self, children, content):
		self.children = children
		self.content = content

	def render(self):
		raise NotImplementedError("node meta-class cannot be evaluated")


class GroupNode(Node):
	def __init__(self, children):
		super().__init__(children, None)

	def render(self, scope={}):
		"Render all children in group."
		ret = ""

		for child in self.children:
			render = child.render(scope)
			if render is None:
				render = ""
			ret += str(render)

		return ret


class TextNode(Node):
	def __init__(self, content):
		super().__init__([], content)

	def render(self, scope={}):
		"Render sanitised content"
		return sanitise(self.content)


class ExprNode(Node):
	def __init__(self, content):
		super().__init__([], content)

	def render(self, scope):
		"Return evaluated content or None"
		try:
			return eval(self.content, {}, scope)
		except:
			return None


class Parser:
	"Main parsing class."
	def __init__(self, tokens):
		self.tokens = tokens

		self.pos = 0
		self.length = len(tokens)

	def end(self):
		return self.pos == self.length

	def peek(self):
		if not self.end():
			return self.tokens[self.pos]

	def next(self):
		if not self.end():
			self.pos += 1

	def _parse_token(self):
		if self.end():
			return None

		# expr
		if self.peek() == "{{":
			self.next()

			expr = ExprNode(self.peek())
			self.next()

			if not expr or self.peek() != "}}":
				raise ParseError("error parsing expression")

			return expr
		# text
		else:
			return TextNode(self.peek())

	def _parse_group(self):
		groups = []

		while not self.end():
			groups.append(self._parse_token())
			self.next()

		groups = [group for group in groups if group]
		return GroupNode(groups)

	def parse(self):
		# EBNF for epyc:
		# group = (token)+
		# token = expr
		# token = text
		# expr  = {{ <any python expression> }}
		# text  = <any text>

		return self._parse_group()

class Tokeniser:
	"Main tokenising class."
	def __init__(self, string):
		self.string = string

	def tokenise(self):
		# TODO: make this nice
		# and make it catch errors
		blocks = re.split("({{)(.*?)(}})", self.string)
		return Parser(blocks)

if __name__ == "__main__":
	string = "\n".join(iter(input, ""))
	print(Tokeniser(string).tokenise().parse().render())
