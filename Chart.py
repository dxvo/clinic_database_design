# Chart library for making report templates easier to make

import random as r

class Chart:
  
  def __init__(self, name, chart_type, chart_label):
    # Display dimensions
    self.width = 500
    self.height = 500
    
    # Title
    self.title_name = name
    self.title_size = 25
    
    # Chart Type
    self.chart_type = chart_type
    
    # Content Labels
    self.chart_label = chart_label
    
    # Data
    self.data_values = []
    self.data_labels = []
    self.data_colors = []
  
  def insert(self, label, value):
    self.data_labels.append(label)
    self.data_values.append(value)
    self.data_colors.append(random_blue())
  
  def get_width(self):
    return str(self.width) + "px"
  
  def get_height(self):
    return str(self.height) + "px"

def random_blue():
  # Produces a random shade of blue for chart content
  
  # Low end of gradient
  dark_r = 15
  dark_g = 15
  dark_b = 25
  
  # High end of gradient
  light_r = 180
  light_g = 230
  light_b = 240
  
  # Pick on gradient
  x = r.random()
  new_r = int(dark_r * x + light_r * (1 -x))
  new_g = int(dark_g * x + light_g * (1 -x))
  new_b = int(dark_b * x + light_b * (1 -x))
  
  # Produce string
  string = "rgba( " + str(new_r) + ", " + str(new_g) + ", " + str(new_b) + ", 0.8)"
  
  return string
  
  
