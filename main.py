import npyscreen 


def heightOfMultiline(self):
    width = self.width 
    print(f"the width is {width}")


class myMultiline(npyscreen.MultiLineEdit):
    def calculate_area_needed(self):
        width = self.space_available()[1]
        lines = self.value.split('\n')

        linesheight = len(lines)

        # for l in lines:
        #     additionalLines = len(l) // width
        #     linesheight += additionalLines 

        # we need `linesheight` height and self.width width 

        return linesheight, width

    def when_value_edited(self):
        print(f"area needed: {self.calculate_area_needed()}")
        self.display()


class nbkCell(npyscreen.BoxTitle):
    #_contained_widget = npyscreen.MultiLineEdit
    _contained_widget = myMultiline

class notebookForm(npyscreen.Form):
    def create(self):
        self.myName = self.add(npyscreen.TitleText, name='Notebook name here')

        self.myDepartment = self.add(npyscreen.TitleText, name='Department')
        self.myDate = self.add(npyscreen.TitleDateCombo, name='Date employed')

        self.debugBox = self.add(npyscreen.MultiLineEdit, name="debug", height=10)

        self.myBox1 = self.add(nbkCell, name="Cell 1", height=9)

        

def myfunction(*args):
    F = notebookForm(name = 'My test app')
    F.edit()

    return f"notebook name: {F.myBox1.width}"

if __name__ == '__main__':
    print(npyscreen.wrapper_basic(myfunction))
