#!/usr/bin/env python
# -*- coding: utf-8 -*-
#https://github.com/KiCad/kicad-library-utils/tree/master/pcb
import sexpr, re

class KicadMod(object):
    """
    A class to parse kicad_mod files format of the KiCad
    """
    def __init__(self, filename):
        self.filename = filename

        self.default_width = 0.15
        # read the s-expression data
        f = open(filename)
        sexpr_data = ''.join(f.readlines())

        # parse s-expr
        sexpr_data = sexpr.parse_sexp(sexpr_data)
        self.sexpr_data = sexpr_data

        # module name
        self.name = self.sexpr_data[1]

        # module layer
        self.layer = self._getValue('layer')

        # locked flag
        self.locked = True if self._hasValue(self.sexpr_data, 'locked') else False

        # description
        self.description = self._getValue('descr')

        # tags
        self.tags = self._getValue('tags')

        # auto place settings
        self.autoplace_cost90 = self._getValue('autoplace_cost90', 0)
        self.autoplace_cost180 = self._getValue('autoplace_cost180', 0)

        # module clearance settings
        self.clearance = self._getValue('clearance', 0)
        self.solder_mask_margin = self._getValue('solder_mask_margin', 0)
        self.solder_paste_margin = self._getValue('solder_paste_margin', 0)
        self.solder_paste_ratio = self._getValue('solder_paste_ratio', 0)

        # attribute
        self.attribute =  self._getValue('attr', 'pth')

        # reference
        self.reference = self._getText('reference')[0]

        # value
        self.value = self._getText('value')[0]

        # user text
        self.userText = self._getText('user')

        # lines
        self.lines = self._getLines()

        # polys
        self.polys = self._getPolys()

        # circles
        self.circles = self._getCircles()

        # arcs
        self.arcs = self._getArcs()

        # pads
        self.pads = self._getPads()

        # models
        self.models = self._getModels()

    # check if value exists in any element of data
    def _hasValue(self, data, value):
        for i in data:
            if type(i) == type([]):
                if self._hasValue(i, value):
                    return True
            elif str(i) == value:
                return True
        return False

    # return the array which has value as first element
    def _getArray(self, data, value, result=None):
        if result is None: result = []
        for i in data:
            if type(i) == type([]):
                self._getArray(i, value, result)
            else:
                if i == value:
                    result.append(data)
        return result

    # update or create an array
    def _updateCreateArray(self, array, place_after=None):
        # check if array exists
        # first element of array is used as key
        # this function only works for arrays which has a single occurrence
        found_array = self._getArray(self.sexpr_data, array[0])
        if found_array:
            index = self.sexpr_data.index(found_array[0])
            self.sexpr_data.pop(index)
            self.sexpr_data.insert(index, array)
        else:
            self._createArray(array, place_after)

    # create an array
    def _createArray(self, new_array, place_after=None):
        # place_after must be an array with the desired position name
        # once the first name match the new array will be placed after
        # the last matched occurrence of the name
        for field in place_after:
            pos_array = self._getArray(self.sexpr_data, field)
            if pos_array:
                index = len(self.sexpr_data) - self.sexpr_data[::-1].index(pos_array[-1]) - 1
                self.sexpr_data.insert(index + 1, new_array)
                break
        else:
            # case doesn't find any desired position, append to end of the array
            self.sexpr_data.append(new_array)

    # return the second element of the array because the array is expected
    # to have the following format: [key value]
    # returns def_value if not field the value
    def _getValue(self, array, def_value=None):
        a = self._getArray(self.sexpr_data, array)
        return def_value if not a else a[0][1]

    def _getText(self, which_text):
        result = []
        for text in self._getArray(self.sexpr_data, 'fp_text'):
            if text[1] == which_text:
                text_dict = {}
                text_dict[which_text] = text[2]

                # text position
                a = self._getArray(text, 'at')[0]
                text_dict['pos'] = {'x':a[1], 'y':a[2], 'orientation':0}
                if len(a) > 3: text_dict['pos']['orientation'] = a[3]

                # text layer
                a = self._getArray(text, 'layer')[0]
                text_dict['layer'] = a[1]

                # text font
                a = self._getArray(text, 'font')[0]
                asize = self._getArray(a, 'size')
                athickness = self._getArray(a, 'thickness')
                if len(asize)>0:
                    a_height = asize[0][1]
                    a_width = asize[0][2]
                else:
                    a_height = 1
                    a_width = 1
                if len(athickness)>0:
                    a_thickness = athickness[0][1]
                else:
                    a_thickness = 1
                text_dict['font'] = {'height':a_height, 'width':a_width, 'thickness':a_thickness}
                text_dict['font']['italic'] = self._hasValue(a, 'italic')

                # text hide
                text_dict['hide'] = self._hasValue(text, 'hide')

                result.append(text_dict)

        return result

    def _addText(self, which_text, data):
        # TODO: should check if all keys of dictionary are valid
        # update the arrays
        for text in data:
            fp_text = ['fp_text', which_text, text[which_text]]

            # text position
            at = ['at', text['pos']['x'], text['pos']['y']]
            if text['pos']['orientation'] != 0: at.append(text['pos']['orientation'])
            fp_text.append(at)

            # layer
            fp_text.append(['layer', text['layer']])

            # text hide
            if text['hide']: fp_text.append('hide')

            # effects
            font = ['font', ['size', text['font']['height'], text['font']['width']], ['thickness', text['font']['thickness']]]
            if text['font']['italic']: font.append('italic')
            fp_text.append(['effects', font])

            # create the array
            self._createArray(fp_text, ['fp_text', 'attr', 'tags', 'descr', 'tedit'])


    def _getLines(self, layer=None):
        lines = []
        for line in self._getArray(self.sexpr_data, 'fp_line'):
            line_dict = {}
            if self._hasValue(line, layer) or layer == None:
                a = self._getArray(line, 'start')[0]
                line_dict['start'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(line, 'end')[0]
                line_dict['end'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(line, 'layer')[0]
                line_dict['layer'] = a[1]
                
                if "width" in line:
                    a = self._getArray(line, 'width')[0]
                    line_dict['width'] = a[1]
                else:
                    line_dict['width'] = self.default_width

                lines.append(line_dict)

        return lines

    def _addLines(self, lines):
        for line in lines:
            fp_line = ['fp_line',
                ['start', line['start']['x'], line['start']['y']],
                ['end', line['end']['x'], line['end']['y']],
                ['layer', line['layer']],
                ['width', line['width']]]

            self._createArray(fp_line, ['fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])

    def _getPolys(self, layer=None):
        polys = []
        for line in self._getArray(self.sexpr_data, 'fp_poly'):
            line_dict = {}
            if self._hasValue(line, layer) or layer == None:
                a = self._getArray(line, 'pts')[0]
                a = self._getArray(a, 'xy')
                pts = []
                for apts in a:
                    p = {'x':apts[1], 'y':apts[2]}
                    pts.append(p)

                line_dict['pts'] = pts

                a = self._getArray(line, 'layer')[0]
                line_dict['layer'] = a[1]

                a = self._getArray(line, 'width')[0]
                line_dict['width'] = a[1]

                polys.append(line_dict)

        return polys

    def _getCircles(self, layer=None):
        circles = []
        for circle in self._getArray(self.sexpr_data, 'fp_circle'):
            circle_dict = {}
            # filter layers, None = all layers
            if self._hasValue(circle, layer) or layer == None:
                a = self._getArray(circle, 'center')[0]
                circle_dict['center'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(circle, 'end')[0]
                circle_dict['end'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(circle, 'layer')[0]
                circle_dict['layer'] = a[1]

                if "width" in circle:
                    a = self._getArray(circle, 'width')[0]
                    circle_dict['width'] = a[1]
                else:
                    circle_dict['width'] = self.default_width
                
                circles.append(circle_dict)

        return circles

    def _addCircles(self, circles):
        for circle in circles:
            fp_circle = ['fp_circle',
                ['center', circle['center']['x'], circle['center']['y']],
                ['end', circle['end']['x'], circle['end']['y']],
                ['layer', circle['layer']],
                ['width', circle['width']]]

            self._createArray(fp_circle, ['fp_circle','fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])

    def _getArcs(self, layer=None):
        arcs = []
        for arc in self._getArray(self.sexpr_data, 'fp_arc'):
            arc_dict = {}
            # filter layers, None = all layers
            if self._hasValue(arc, layer) or layer == None:
                a = self._getArray(arc, 'start')[0]
                arc_dict['start'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(arc, 'end')[0]
                arc_dict['end'] = {'x':a[1], 'y':a[2]}

                a = self._getArray(arc, 'angle')[0]
                arc_dict['angle'] = a[1]

                a = self._getArray(arc, 'layer')[0]
                arc_dict['layer'] = a[1]

                if "width" in arc:
                    a = self._getArray(arc, 'width')[0]
                    arc_dict['width'] = a[1]
                else:
                    arc_dict['width'] = self.default_width

                arcs.append(arc_dict)

        return arcs

    def _addArcs(self, arcs):
        for arc in arcs:
            fp_arc = ['fp_arc',
                ['start', arc['start']['x'], arc['start']['y']],
                ['end', arc['end']['x'], arc['end']['y']],
                ['angle', arc['angle']],
                ['layer', arc['layer']],
                ['width', arc['width']]]

            self._createArray(fp_arc, ['fp_arc', 'fp_circle','fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])

    def _getPads(self):
        pads = []
        for pad in self._getArray(self.sexpr_data, 'pad'):
            # number, type, shape
            pad_dict = {'number':pad[1], 'type':pad[2], 'shape':pad[3]}

            # position
            a = self._getArray(pad, 'at')[0]
            pad_dict['pos'] = {'x':a[1], 'y':a[2], 'orientation':0}
            if len(a) > 3: pad_dict['pos']['orientation'] = a[3]

            # size
            a = self._getArray(pad, 'size')[0]
            pad_dict['size'] = {'x':a[1], 'y':a[2]}

            # layers
            a = self._getArray(pad, 'layers')[0]
            pad_dict['layers'] = a[1:]

            # rect delta
            pad_dict['rect_delta'] = {}
            a = self._getArray(pad, 'rect_delta')
            if a: pad_dict['rect_delta'] = a[0][1:]

            # drill
            pad_dict['drill'] = {}
            drill = self._getArray(pad, 'drill')
            if drill:
                # there is only one drill per pad
                drill = drill[0]

                # offset
                pad_dict['drill']['offset'] = {}
                offset = self._getArray(drill, 'offset')
                if offset:
                    offset = offset[0]
                    pad_dict['drill']['offset'] = {'x':offset[1], 'y':offset[2]}
                    drill.remove(offset)

                # shape
                if self._hasValue(drill, 'oval'):
                    drill.remove('oval')
                    pad_dict['drill']['shape'] = 'oval'
                else:
                    pad_dict['drill']['shape'] = 'circular'

                # size
                pad_dict['drill']['size'] = {}
                if len(drill) > 1:
                    x = drill[1]
                    y = drill[2] if len(drill) > 2 else x
                    pad_dict['drill']['size'] = {'x':x, 'y':y}

            # die length
            pad_dict['die_length'] = {}
            a = self._getArray(pad, 'die_length')
            if a: pad_dict['die_length'] = a[0][1]

            ## clearances zones settings
            # clearance
            pad_dict['clearance'] = {}
            a = self._getArray(pad, 'clearance')
            if a: pad_dict['clearance'] = a[0][1]
            # solder mask margin
            pad_dict['solder_mask_margin'] = {}
            a = self._getArray(pad, 'solder_mask_margin')
            if a: pad_dict['solder_mask_margin'] = a[0][1]
            # solder paste margin
            pad_dict['solder_paste_margin'] = {}
            a = self._getArray(pad, 'solder_paste_margin')
            if a: pad_dict['solder_paste_margin'] = a[0][1]
            # solder paste margin ratio
            pad_dict['solder_paste_margin_ratio'] = {}
            a = self._getArray(pad, 'solder_paste_margin_ratio')
            if a: pad_dict['solder_paste_margin_ratio'] = a[0][1]

            ## copper zones settings
            # zone connect
            pad_dict['zone_connect'] = {}
            a = self._getArray(pad, 'zone_connect')
            if a: pad_dict['zone_connect'] = a[0][1]
            # thermal width
            pad_dict['thermal_width'] = {}
            a = self._getArray(pad, 'thermal_width')
            if a: pad_dict['thermal_width'] = a[0][1]
            # thermal gap
            pad_dict['thermal_gap'] = {}
            a = self._getArray(pad, 'thermal_gap')
            if a: pad_dict['thermal_gap'] = a[0][1]

            pads.append(pad_dict)

        return pads

    def _addPads(self, pads):
        for p in pads:
            # number, type, shape
            pad = ['pad', p['number'], p['type'], p['shape']]

            # position
            at = ['at', p['pos']['x'], p['pos']['y']]
            if p['pos']['orientation'] != 0: at.append(p['pos']['orientation'])
            pad.append(at)

            # size
            pad.append(['size', p['size']['x'], p['size']['y']])

            # drill
            if p['drill']:
                drill = ['drill']

                # drill shape
                if p['drill']['shape'] == 'oval':
                    drill += ['oval']

                # drill size
                if p['drill']['size']:
                    drill += [p['drill']['size']['x']]

                    # if shape is oval has y size
                    if p['drill']['shape'] == 'oval':
                        drill += [p['drill']['size']['y']]

                # drill offset
                if p['drill']['offset']:
                    drill.append(['offset', p['drill']['offset']['x'], p['drill']['offset']['y']])

                pad.append(drill)

            # layers
            pad.append(['layers'] + p['layers'])

            # die length
            if p['die_length']:
                pad.append(['die_length', p['die_length']])

            # rect_delta
            if p['rect_delta']:
                pad.append(['rect_delta'] + p['rect_delta'])

            ## clearances zones settings
            # clearance
            if p['clearance']:
                  pad.append(['clearance', p['clearance']])
            # solder mask margin
            if p['solder_mask_margin']:
                  pad.append(['solder_mask_margin', p['solder_mask_margin']])
            # solder paste margin
            if p['solder_paste_margin']:
                  pad.append(['solder_paste_margin', p['solder_paste_margin']])
            # solder paste margin ratio
            if p['solder_paste_margin_ratio']:
                  pad.append(['solder_paste_margin_ratio', p['solder_paste_margin_ratio']])

            ## copper zones settings
            # zone connect
            if p['zone_connect']:
                  pad.append(['zone_connect', p['zone_connect']])
            # thermal width
            if p['thermal_width']:
                  pad.append(['thermal_width', p['thermal_width']])
            # thermal gap
            if p['thermal_gap']:
                  pad.append(['thermal_gap', p['thermal_gap']])

            self._createArray(pad, ['pad', 'fp_arc', 'fp_circle','fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])

    def _getModels(self):
        models_array = self._getArray(self.sexpr_data, 'model')

        models = []
        for model in models_array:
            model_dict = {'file':model[1]}

            # position
            xyz = self._getArray(self._getArray(model, 'at'), 'xyz')[0]
            model_dict['pos'] = {'x':xyz[1], 'y':xyz[2], 'z':xyz[3]}

            # scale
            xyz = self._getArray(self._getArray(model, 'scale'), 'xyz')[0]
            model_dict['scale'] = {'x':xyz[1], 'y':xyz[2], 'z':xyz[3]}

            # rotate
            xyz = self._getArray(self._getArray(model, 'rotate'), 'xyz')[0]
            model_dict['rotate'] = {'x':xyz[1], 'y':xyz[2], 'z':xyz[3]}

            models.append(model_dict)

        return models

    def _addModels(self, models):
        for model in models:
            m = ['model', model['file'],
                ['at', ['xyz', model['pos']['x'], model['pos']['y'], model['pos']['z']]],
                ['scale', ['xyz', model['scale']['x'], model['scale']['y'], model['scale']['z']]],
                ['rotate', ['xyz', model['rotate']['x'], model['rotate']['y'], model['rotate']['z']]]
                ]

            self._createArray(m, ['model', 'pad', 'fp_arc', 'fp_circle','fp_line', 'fp_text', 'attr', 'tags', 'descr', 'tedit'])

    def setAnchor(self, anchor_point):
        # change reference position
        self.reference['pos']['x'] -= anchor_point[0]
        self.reference['pos']['y'] -= anchor_point[1]

        # change value position
        self.value['pos']['x'] -= anchor_point[0]
        self.value['pos']['y'] -= anchor_point[1]

        # change user text position
        for text in self.userText:
            text['pos']['x'] -= anchor_point[0]
            text['pos']['y'] -= anchor_point[1]

        # change lines position
        for line in self.lines:
            line['start']['x'] -= anchor_point[0]
            line['end']['x'] -= anchor_point[0]
            line['start']['y'] -= anchor_point[1]
            line['end']['y'] -= anchor_point[1]

        # change circles position
        for circle in self.circles:
            circle['center']['x'] -= anchor_point[0]
            circle['end']['x'] -= anchor_point[0]
            circle['center']['y'] -= anchor_point[1]
            circle['end']['y'] -= anchor_point[1]

        # change arcs position
        for arc in self.arcs:
            arc['start']['x'] -= anchor_point[0]
            arc['end']['x'] -= anchor_point[0]
            arc['start']['y'] -= anchor_point[1]
            arc['end']['y'] -= anchor_point[1]

        # change pads positions
        for pad in self.pads:
            pad['pos']['x'] -= anchor_point[0]
            pad['pos']['y'] -= anchor_point[1]

    def filterLines(self, layer):
        lines = []
        for line in self.lines:
            if line['layer'] == layer:
                lines.append(line)

        return lines

    def filterCircles(self, layer):
        circles = []
        for circle in self.circles:
            if circle['layer'] == layer:
                circles.append(circle)

        return circles

    def filterArcs(self, layer):
        arcs = []
        for arc in self.arcs:
            if arc['layer'] == layer:
                arcs.append(arc)

        return arcs

    def filterGraphs(self, layer):
        return (self.filterLines(layer) +
                self.filterCircles(layer) +
                self.filterArcs(layer))

    def getPadsByNumber(self, pad_number):
        pads = []
        for pad in self.pads:
            if pad['number'] == pad_number:
                pads.append(pad)

        return pads

    def filterPads(self, pad_type):
        pads = []
        for pad in self.pads:
            if pad['type'] == pad_type:
                pads.append(pad)

        return pads

    def padsBounds(self):
        lower_x = lower_y = 1.0E99
        higher_x = higher_y = -1.0E99

        for pad in self.pads:
            if pad['pos']['x'] < lower_x: lower_x = pad['pos']['x']
            if pad['pos']['x'] > higher_x: higher_x = pad['pos']['x']

            if pad['pos']['y'] < lower_y: lower_y = pad['pos']['y']
            if pad['pos']['y'] > higher_y: higher_y = pad['pos']['y']

        return {'lower':{'x':lower_x, 'y':lower_y},
                'higher':{'x':higher_x, 'y':higher_y}}

    def save(self, filename=None):
        if not filename: filename = self.filename

        # module name
        self.sexpr_data[1] = self.name

        # locked flag
        try:
            self.sexpr_data.remove('locked')
        except ValueError:
            pass
        if self.locked:
            self.sexpr_data.insert(2, 'locked')

        # description
        if self.description: self._updateCreateArray(['descr', self.description], ['tedit'])

        # tags
        if self.tags: self._updateCreateArray(['tags', self.tags], ['descr', 'tedit'])

        # auto place settings
        if self.autoplace_cost90: self._updateCreateArray(['autoplace_cost90', self.autoplace_cost90], ['tags', 'descr', 'tedit'])
        if self.autoplace_cost180: self._updateCreateArray(['autoplace_cost180', self.autoplace_cost180], ['tags', 'descr', 'tedit'])

        # module clearance settings
        if self.clearance: self._updateCreateArray(['clearance', self.clearance], ['tags', 'descr', 'tedit'])
        if self.solder_mask_margin: self._updateCreateArray(['solder_mask_margin', self.solder_mask_margin], ['tags', 'descr', 'tedit'])
        if self.solder_paste_margin: self._updateCreateArray(['solder_paste_margin', self.solder_paste_margin], ['tags', 'descr', 'tedit'])
        if self.solder_paste_ratio: self._updateCreateArray(['solder_paste_ratio', self.solder_paste_ratio], ['tags', 'descr', 'tedit'])

        # attribute
        attr = self.attribute.lower()
        assert attr in ['pth', 'smd', 'virtual'], "attribute must be one of the following options: 'pth', 'smd', 'virtual'"
        # when the footprint is PTH the attr isn't explicitly defined, thus the field attr doesn't exists
        try:
            self.sexpr_data.remove(self._getArray(self.sexpr_data, 'attr')[0])
        except IndexError:
            pass
        # create the field attr if not pth
        if attr != 'pth': self._updateCreateArray(['attr', attr], ['tags', 'descr', 'tedit'])

        # remove all existing text arrays
        for text in self._getArray(self.sexpr_data, 'fp_text'):
            self.sexpr_data.remove(text)
        # reference
        self._addText('reference', [self.reference])
        # value
        self._addText('value', [self.value])
        # user text
        self._addText('user', self.userText)

        # lines
        # remove all existing lines arrays
        for line in self._getArray(self.sexpr_data, 'fp_line'):
            self.sexpr_data.remove(line)
        self._addLines(self.lines)

        # circles
        # remove all existing circles arrays
        for circle in self._getArray(self.sexpr_data, 'fp_circle'):
            self.sexpr_data.remove(circle)
        self._addCircles(self.circles)

        # arcs
        # remove all existing arcs arrays
        for arc in self._getArray(self.sexpr_data, 'fp_arc'):
            self.sexpr_data.remove(arc)
        self._addArcs(self.arcs)

        # pads
        # remove all existing pads arrays
        for pad in self._getArray(self.sexpr_data, 'pad'):
            self.sexpr_data.remove(pad)
        self._addPads(self.pads)

        # models
        # remove all existing models arrays
        for model in self._getArray(self.sexpr_data, 'model'):
            self.sexpr_data.remove(model)
        self._addModels(self.models)

        # convert array data to s-expression and save in the disc
        output = sexpr.build_sexp(self.sexpr_data)
        output = sexpr.format_sexp(output, max_nesting=1)
        f = open(filename, 'w')
        f.write(output)
        f.close()


if __name__ == '__main__':
#    module = KicadMod('/tmp/SOT-23.kicad_mod')
#    module = KicadMod('/tmp/USB_A_Vertical.kicad_mod')
    module = KicadMod('D:\\foot\\QMS-1X52-FEMALE-SMD.kicad_mod')

    import pprint
    #pprint.pprint(module.sexpr_data)
    #pprint.pprint(fp_poly)
    #pprint.pprint(fp_poly[1][1])
    pprint.pprint(module.userText)
    #module.save('/tmp/SATA-7_SMD.kicad_mod.output')
    #module.save('d:\\x.kicad_mod')
