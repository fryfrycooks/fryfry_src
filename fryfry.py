import argparse
import logging
import pandas as pd

table_header_template = """
<div class="fft-wrap">
<table class="fft">
<tbody>
"""

table_close_template = """
</tbody>
</table>
</div>
"""

def main():

	p = argparse.ArgumentParser()
	p.add_argument('-s', '--src')
	p.add_argument('-o', '--output')
	p.add_argument('-p', '--print', default=True)
	a = p.parse_args()

	print (a.src)

	data = parseFromPath(a.src)
	mise_html = buildMiseTable(data['mise'])

	if 'tools' in data:
		tools_html = buildToolsTable(data['tools'])
	else:
		tools_html = ''

	steps_html = buildStepsTable(data['steps'])

	if a.print:
		print ('<hr/>', mise_html)
		print ('<hr/>', tools_html)
		print ('<hr/>', steps_html, '<hr/>')

	if a.output != None:
		with open(a.output, 'w') as f:
			f.write('<hr/>\n')
			f.write(mise_html)
			f.write('<hr/>\n')
			f.write(tools_html)
			f.write('<hr/>\n')
			f.write(steps_html)
			f.write('<hr/>\n')




def parseFromPath(path):

	mise = []
	tools = []
	steps = []

	data = {'mise':[], 'tools':[],'steps':[]}

	with open(path) as f:
		for l in f:
			d = l.strip().split('|')
			if d[0] in data:
				data[d[0]].append(d[1:])
			else:
				logging.error('bad line found %s', l)

	#print (data)
	return data

def writeMiseCell(cell):

	r = '<td class="fft-c-bright">%s</td>\n'
	l = '<td class="fft-c-bleft">%s</td>\n'

	a_s = ''
	if cell['Amount'] != None:
		a_s += cell['Amount']
	if cell['Size'] != None:
		a_s += ' ' + cell['Size']

	i_s = ''
	if cell['Ingredient'] != None:
		i_s += cell['Ingredient']
	if cell['Prep'] != None:
		if len(i_s) > 0:
			i_s += ', '
		i_s += cell['Prep']

	o = r + l 
	o = o % (a_s, i_s)
	return o	

def writeMiseHeaderCell(cell_type):
	return '<td class="fft-g-head" colspan="2">%s</td>\n' % (cell_type.upper())

def writeMiseEmptyCell():
	return '<td class="fft-c-bright"></td>\n<td class="fft-c-bleft"></td>\n'

def buildMiseTable(data):

	df = pd.DataFrame(data, columns=['Type', 'Amount', 'Size', 'Ingredient', 'Prep'])

	right_len = 0
	left_len = 0

	right_idxs = []
	left_idxs = []

	# we have a 2 column table, determine how to balance that table best
	# the left side should be >= the right side
	mc = df['Type'].value_counts()
	mc.sort_values(ascending=False)
	for i, r in mc.iteritems():
		if left_len == right_len or left_len < right_len:
			left_idxs.append(i)
			left_len += r + 1
		else:
			right_idxs.append(i)
			right_len += r + 1

	left_elements = []
	right_elements = []

	#sort the dataframe according to the columns, this will help us create a stack
	#of rows to format
	df.Type = df.Type.astype("category")
	df.Type.cat.set_categories(left_idxs + right_idxs, inplace=True)
	df.sort_values(['Type'])

	last_left_type = ''
	last_right_type = ''

	# build a list of tuples we can iterate through along with header cells
	for i, r in df.iterrows():
		if r['Type'] in left_idxs:

			if r['Type'] != last_left_type:
				left_elements.append({'Type':'#HEADERCELL', 'Title':r['Type']})
				last_left_type = r['Type']
			
			left_elements.append(r)

		else:
			if r['Type'] != last_right_type:
				right_elements.append({'Type':'#HEADERCELL', 'Title':r['Type']})
				last_right_type = r['Type']

			right_elements.append(r)

	elements = []
	for i in range(len(left_elements)):
		if i >= len(right_elements):
			re = {'Type':'#CELLEMPTY'}
		else:
			re = right_elements[i]
		elements.append((left_elements[i], re))


	#now we can build the table
	output = table_header_template[:]
	output += '<tr>\n<th class="fft-sec-head" colspan="4">Mise en Place</th>\n</tr>'

	for l_e, r_e in elements:

		output += '<tr>\n'

		def processElement(elem):
			if elem['Type'] == '#HEADERCELL':
				return writeMiseHeaderCell(elem['Title'])
			elif elem['Type'] == '#CELLEMPTY':
				return writeMiseEmptyCell()
			else:
				return writeMiseCell(elem)

		output += processElement(l_e)
		output += processElement(r_e)

		output += '</tr>\n'

	output = output[:-1]
	output += table_close_template[:]

	return output

def buildToolsTable(data):

	df = pd.DataFrame(data, columns=['Amount', 'Item', 'Prep'])

	output = table_header_template[:]
	output += '<tr>\n<th class="fft-sec-head" colspan="2">Equipment</th>\n</tr>\n'

	for i, r in df.iterrows():

		output += '<tr>\n'

		if r['Amount'] != None:
			output += '<td class="fft-c-bright">%s</td>\n' % (r['Amount'])
		else:
			output += '<td class="fft-c-bright"></td>\n'


		s = ''
		if r['Item'] != None:
			s += r['Item']
		if r['Prep'] != None:
			if len(s) > 0:
				s += ', '
			s += r['Prep']

		output += '<td class="fft-c-bleft">%s</td>\n</tr>\n' % (s)

	output = output[:-1]
	output += table_close_template[:]
	return output

def buildStepsTable(data):

	df = pd.DataFrame(data, columns=['Step', 'Directions'])

	output = table_header_template[:]
	output += '<tr>\n<th class="fft-sec-head" colspan="2">Directions</th>\n</tr>\n'
	output += '<tr>\n<td class="fft-g-head">Step</td>\n<td class="fft-g-head">Action</td>\n</tr>\n'

	for i, r in df.iterrows():
		output += '<tr>\n'
		output += '<td class="fft-c-cell">%s</td>\n' % (r['Step'])
		output += '<td class="fft-c-cell">%s</td>\n' % (r['Directions'])
		output += '</tr>\n'

	output = output[:-1]
	output += table_close_template[:]
	return output


if __name__ == "__main__":
	main()





