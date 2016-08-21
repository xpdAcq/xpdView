# Adding functions in a live ipython session

1. Define a function within the ipython session
  * The function must have an argument that takes in the image array and it must return a scalar.
  * ex:
``` python
def ex_func(arr):
      num = 0
      for i in arr[0]:
        for j in arr[1]:
          num += j
      return num
```

2. Add the function to the function dictionary
  * Assuming that the display object is named `display`, you add the function like so: `display.add_func(ex_func)`

# Adding functions in bulk
1. If you want to add multiple functions at a time, add them all to a list and pass the list to `display.add_many_func(list)` like so:
``` python
func_list = [func_1, func_2, func_3]
display.add_many_func(func_list)
```

# Removing functions  
1. Functions can be removed in much the same way as adding them: `display.remove_func(ex_func)`
