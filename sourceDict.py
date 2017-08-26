# encoding:utf-8


def generateSourcefile(glossaryfile, xiepeiyidic, sourcefile):
    with open(glossaryfile, 'rt') as greader, open(xiepeiyidic, 'rt') as xreader, open(sourcefile, 'wt') as writer:
        glines = greader.readlines()
        xlines = xreader.readlines()
        for gl in glines:
            gl = gl.split()
            pos = gl[1]
            gl = gl[0]
            if pos == 'V':
                for xl in xlines:
                    writer.write(gl + '\t' + xl)


if '__main__' == __name__:
    glossaryfile = './hownet/glossary.dat'
    xiepeiyidic = './result/bt_xiepeiyiVerb.dic'
    sourcefile = './result/im_sourcefile.dat'

    generateSourcefile(glossaryfile, xiepeiyidic, sourcefile)
