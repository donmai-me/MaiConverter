# Introduction
Are you a depraved charter tired of making Simai charts by hand on your text editor? Or are you a new Maimai charter that feels intimidated by Simai's convoluted format? Do you want to focus on writing charts by adding notes with only the required information? Suppose you don't mind using the command line. In that case, you can use MaiConverter to make and export your Simai (and other chart formats) easily.

> Note: This isn't a full documentation/walkthough of every feature in the SimaiChart class in MaiConverter. You are encouraged to read the source files to get a better understanding of MaiConverter (and so you can help me document the code.)

# Import your existing chart
To import an existing chart, strip all Simai metadata until you're left with only the chart text. One chart difficulty at a time and no `&inote=`s. Save this as a separate file and import it to Simai.

```python
>>> from maiconverter.simai import SimaiChart
>>> with open("simai_chart.txt", "r") as f:
...     text = f.read()
...
>>> simai = SimaiChart.from_str(text)
```

Suppose there are no errors during parsing. Then you're left with a SimaiChart instance that has all your work imported.

# Chart from scratch
If you want to start from scratch, then import SimaiChart and make an instance.

```python
>>> from maiconverter.simai import SimaiChart
>>> simai = SimaiChart()
```

# Setting BPMs
If you're starting from scratch, you should first set your starting BPM. First, specify the measure the BPM takes effect, then the BPM. Let's define the starting BPM as 220:

```python
>>> simai.set_bpm(1.0, 220)
```

Should you change your mind, you can use `set_bpm` again, and it will automatically overwrite the previously set BPM.

```python
>>> simai.set_bpm(1.0, 300)
```

You can remove a BPM change by using `del_bpm`, providing only the measure of the BPM change.

```python
# Change BPM to 200 at measure 13
>>> simai.set_bpm(13, 200.0)
# Oops we meant measure 14
>>> simai.del_bpm(13)
>>> simai.set_bpm(14, 200)
```

# Adding (and deleting) notes
**NOTE**: Although the Simai buttons and touch screen locations start at 1 and end at 8, MaiConverter begins at 0 and ends at 7. Why? Because I'm a programmer, and the arcade chart formats also start at 0. MaiConverter automatically adds 1 to every button when exporting.

```python
# Add an ex tap note for first measure in button 0 and a hold note at measure 1.5 at button 5 for 0.25 measures
>>> simai.add_tap(1.0, 0, is_ex=True)
>>> simai.add_hold(1.5, 5, 0.25)
...
# Add a > slide at measure 50.5 from button 5 to 1 with a duration of 0.75 measures.
>>> simai.add_tap(50.5, 5, is_star=True)
>>> simai.add_slide(50.5, 5, 1, 0.75, ">")
# Add a touch tap note in measure 70, at E5
>>> simai.add_touch_tap(70, 5, "E")
# Add a firework touch hold note in measure 70.5, at C with a duration of 1 measure.
>>> simai.add_touch_hold(70.5, 0, "C", 1, is_firework=True)
```

If you don't know the order of arguments of an `add` function, then invoke the function using keywords. Invoking an `add` function with keyworded arguments is recommended for frontend programs.

```python
# Add an ex tap note for first measure in button 0 and a hold note at measure 1.5 at button 5 for 0.25 measures
>>> simai.add_tap(measure=1.0, position=0, is_ex=True)
>>> simai.add_hold(measure=1.5, position=5, duration=0.25)
...
# Add a > slide at measure 50.5 from button 5 to 1 with a duration of 0.75 measures.
>>> simai.add_tap(measure=50.5, position=5, is_star=True)
>>> simai.add_slide(measure=50.5, start_postion=5, end_position=1, duration=0.75, pattern=">")
# Add a touch tap note in measure 70, at E5
>>> simai.add_touch_tap(measure=70, position=5, region="E")
# Add a firework touch hold note in measure 70.5, at C with a duration of 1 measure.
>>> simai.add_touch_hold(measure=70.5, position=0, region="C", duration=1, is_firework=True)
```

For every `add_tap` and `add_slide` functions, there are corresponding `del_tap` and `del_slde` functions. The only parameters that the del functions need are the measure and button where a note happened. For `del_touch_tap` and `del_touch_hold` functions, the measure, location, and touch region are required.

```python
# Delete tap note at measure 6.125 at button 0
>>> simai.delete_tap(6.125, 0)
# Delete hold note starting at measure 12 at button 5
>>> simai.delete_hold(12, 5)
# Delete slide note starting at measure 9, starting at button 2, ending at button 7
>>> simai.delete_slide(9, 2, 7)
```
