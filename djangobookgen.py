import os

from subprocess import Popen
# taken from:
# http://www.swag.dk/pub/djangobook-pdf/
# needs pdftk and htmldoc installed

pdfs = []

for i in xrange(1, 21):
    p = Popen(['htmldoc', '--webpage', '-f', '%d.pdf' % i, 
            'http://www.djangobook.com/en/2.0/chapter%02d/' % i])
    p.wait()

    if p.returncode == 0:
        if os.path.exists('%d.pdf' % i):
            pdfs.append('%d.pdf' % i)

if len(pdfs) > 0:
    cmds = ['pdftk']
    cmds.extend(pdfs)
    cmds.extend(['cat', 'output', 'djangobook_all.pdf'])
    p = Popen(cmds)
    p.wait()
