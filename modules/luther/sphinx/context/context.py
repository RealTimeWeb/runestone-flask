# Copyright (C) 2011  Bradley N. Miller
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
__author__ = 'acbart'

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive


def setup(app):
    app.add_directive('context', ContextDirective)

    app.add_node(ContextNode, html=(visit_context_node, depart_context_node))

    #app.add_javascript('context.js')
    #app.add_stylesheet('context.css')


BEGIN = """ <div id='%(divid)s' class='context alert alert-warning'> """

BEGIN_FORM = """
    <form id='%(divid)s_context' name='%(divid)s_context' action="">
        <fieldset>
            <legend>Context</legend>
            <div class='context-question'>%(content)s</div>
            <div id='%(divid)s_context_input'>
                <div class='context-options'>
"""

CONTEXT_ELEMENT = """
<label class='radio-inline'>
    <input type='radio' name='%(divid)s_opt' id='%(divid)s_%(value)s' value='%(value)s'>
    %(value)s
</label>
"""

END_CONTEXT_OPTIONS = """ </div> """

COMMENT = """
<br />
<input type='text' class='form-control' style='width:300px;' name='%(divid)s_comment' placeholder='Any comments?'>
<br />
"""

END_CONTEXT_INPUT = """
            <button type='button' id='%(divid)s_submit' class='btn btn-success' onclick="submitContext('%(divid)s');">Submit</button>
        </div>
"""

END_FORM = """
        </fieldset>
    </form>
"""

RESULTS_DIV = """ <div id='%(divid)s_results'></div> """



END = """
    <script type='text/javascript'>
        // check if the user has already answered this context
        $(function() {
            var len = localStorage.length;
            if (len > 0) {
                for (var i = 0; i < len; i++) {
                    var key = localStorage.key(i);
                    if (key === '%(divid)s') {
                        var ex = localStorage.getItem(key);
                        if(ex === "true") {
                            // hide the context inputs
                            $("#%(divid)s_context_input").hide();

                            // show the results of the context
                            var data = {};
                            data.div_id = '%(divid)s';
                            data.course = eBookConfig.course;
                            jQuery.get(eBookConfig.ajaxURL+'getcontextresults', data, showContextResults);
                        }
                    }
                }
            }
        });
    </script>
</div>
"""

class ContextNode(nodes.General, nodes.Element):
    def __init__(self, options):
        super(ContextNode, self).__init__()
        self.contextnode_components = options

def visit_context_node(self, node):
    res = BEGIN
    res += BEGIN_FORM

    for i in range(1, node.contextnode_components['scale']+1):
        res += CONTEXT_ELEMENT % {'divid':node.contextnode_components['divid'], 'value':i}

    res += END_CONTEXT_OPTIONS

    if 'allowcomment' in node.contextnode_components:
        res += COMMENT

    res += END_CONTEXT_INPUT
    res += END_FORM
    res += RESULTS_DIV
    res += END

    res = res % node.contextnode_components
    self.body.append(res)

def depart_context_node(self,node):
    pass


class ContextDirective(Directive):
    required_arguments = 1  # the div id
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {'scale':directives.positive_int,
                   'allowcomment': directives.flag}

    node_class = ContextNode

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        
        self.options['divid'] = self.arguments[0]
        self.options['content'] = "<p>".join(self.content)
        context_node = ContextNode(self.options)

        return [context_node]


