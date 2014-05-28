Introduction
------------

Computer Science is about solving problems at scale. <--- Explain creativity as being outside this paradigm, but still cover it

Computers are a tool for this, because they are exceptionally good at automating tasks

When reading this book, think about how we identify and design Problems, Data, and Algorithms

Contextual Learning
-------------------

This textbook is designed to be contextualized. That means that when we introduce a concept, it will be connected to ideas and framed by problems that are authentic to you. Think of it as a "Choose-your-own Adventure" story. At any time, you can look at a parallel example in another discipline.

Problems
--------

What kinds of problems can we solve in Computer Science? Here's some simple criteria:

* **Big**: The problem has many complicated parts, or involves a lot of data.
* **Repeated**: The problem needs to be done many times.

When deciding whether you should use Computational Thinking to solve a problem, you need to consider how big and how often. Sorting your socks is not a problem that should be solved with Computational Thinking, unless you are constantly washing hundreds of socks.

Of course, there are other reasons why problems might not be solvable with Computational Thinking. Mathematicians have proven that some problems are impossible to compute solutions to. Sometimes problems would take so long to solve, we'd run out of time in the universe. Sometimes problems require buy-in from people that aren't interested.

Still, there are many problems that are easy to solve with a computer.


.. context:: pollid1
   :scale: 10
   :allowcomment:

    On a scale from 1 to 10, how important do you think it is to have a polling directive in the Runestone Tools?
    
Blockly
-------

.. blockly:: blockly1

   * controls
   controls_if
   controls_repeat_ext
   ====
   * logic
   logic_compare
   ====
   * math
   math_number
   math_arithmetic
   ====
   * text
   text
   text_print
   ====
   variables

   preload::
   <xml>  
      <block type="variables_set" id="1" inline="true" x="25" y="9">    
         <field name="VAR">X</field>    
         <value name="VALUE">      
            <block type="math_number" id="2">
               <field name="NUM">10</field>
            </block>    
         </value>  
      </block>
   </xml>

Data
----

.. fillintheblank:: baseconvert1
   :correct: \\b31\\b
   :blankid: baseconvert1_ans1

   What is value of 25 expressed as an octal number (base 8) :textfield:`baseconvert1_ans1::mini`

Algorithms
----------

.. mchoicemf:: question1_1
   :answer_a: Python
   :answer_b: Java
   :answer_c: C
   :answer_d: ML
   :correct: a
   :feedback_a: Yes, Python is a great language to learn, whether you are a beginner or an experienced programmer.
   :feedback_b: Java is a good object oriented language but it has some details that make it hard for the beginner.
   :feedback_c: C is an imperative programming language that has been around for a long time, but it is not the one that we use.
   :feedback_d: No, ML is a functional programming language.  You can use Python to write functional programs as well.

   What programming language does this site help you to learn?

Creativity
----------

Of course, data is beautiful.

Looking at visualizations of data can activate the same neural circuitry as traditional works of art. [Citation]
