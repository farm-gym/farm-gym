


## Farm

### Farm  configuration
Let us configure a simple farm farm0.yaml as follows:  
```yaml
Farm:
  Field-0:
    localization:
      latitude#°: 50.62
      longitude#°: 3.05
      altitude#m: 10
    shape:
      length#nb: 1
      width#nb: 1
      scale#m: 1.0
    entities:
      - Weather: lille
      - Soil:  clay
      - Plant: bean
      - Pollinators: bee
  Farmer-0:
    type: basic
    parameters:
      max_daily_interventions: 1
      max_daily_observations: 2
day_path: {"field":"Field-0", "entity":"Weather-0", "variable": "day#int365"}
actions: actions.yaml
score: score.yaml
initialization: init.yaml
interaction_mode: POMDP
```
Note that we can easily modify the specification of the weather to another one such as lille2, lille3, montpellier, etc (see below).
In the current model,  presence of a pollinator is important for the growth of bean fruits.
### Initialization
We can define an initialization file farm0_init.yaml as follows:
```yaml
Initial:
  Field-0:
    Weather-0:
      year#int100: 0
      day#int365: 120
    Soil-0:
      microlife_health_index#%: 75
    Plant-0:
      stage: "seed"
      population#nb: 1
Terminal:
  [
    [{state_variable: ["Field-0", "Weather-0", "day#int365", []], function: "value", operator: ">=", ref_value: 360}]
  ]
```
Note that by changing the population#nb to 0 we simply have an empty field.

### Actions
The file farm0_actions.yaml may look like this:
```yaml
params:
  max_action_schedule_size: 1
  number_of_bins_to_discretize_continuous_actions: 11
observations:
  Free:
    Field-0:
      Weather-0:
        day#int365: 
        air_temperature: 
          '*':
interventions:
  BasicFarmer-0:
    Field-0:
      Soil-0:
        water_discrete: 
          plot: ['(0, 0)']
          amount#L: [5.0]
```
Note that this allows a single action: watering 5L of water. By changing the amount#L to another list, [2,3,5] we enable 3 actions,
and we can put [0.] to force no watering, or alternatively delete the corresponding action.

We can define a score, we keep it as it is for now.

## Monitoring

Now that we have defined a farm, we can run some experiments:

```python
def env():
    yaml_path = os.path.join(os.path.dirname(__file__), "farm0.yaml")
    farm = make_farm(yaml_path)

    farm.add_monitoring(
        make_variables_to_be_monitored(
            [
                "f0>weather>rain_amount#mm.day-1",
                "f0>weather>clouds#%",
                "f0>weather>air_temperature>mean#°C",
                "f0>weather>wind>speed#km.h-1",
                "f0>soil>available_Water#L",
                "f0>soil>microlife_health_index#%",
                "f0>soil>available_N#g",
                "f0>soil>available_P#g",
                "f0>soil>available_K#g",
                "f0>soil>available_C#g",
                "f0>plant>size#cm",
                "f0>plant>cumulated_stress_water#L",
                "f0>plant>cumulated_stress_nutrients_N#g",
                "f0>plant>cumulated_stress_nutrients_P#g",
                "f0>plant>cumulated_stress_nutrients_K#g",
                "f0>plant>cumulated_stress_nutrients_C#g",
                # "f0>plant>flowers_per_plant#nb@mat",
                "f0>plant>flowers_per_plant#nb",
                "f0>plant>fruits_per_plant#nb",
                "f0>plant>fruit_weight#g",
                "f0>plant>stage@name",
            ]
        )
    )

    return farm


if __name__ == "__main__":
    f = env()
    print(f)
    agent = Farmgym_RandomAgent()
    run_gym_xp(f, agent, max_steps=250, render="text&image")
```
Note that we have defined here a bunch of variables to be monitored.
Some of them are scalars, some are vectors (with one component for each plot in the field).
By default, vectors are aggregated by computing the mean value over the components. We may use other functions.
For instance  @mat in "f0>plant>flowers_per_plant#@mat"  indicates to represent the vector with a matrix, later displayed as a 2d image.

The function run_gym_xp  generates a full trajectory of interaction with the farm. The rendering option "text&image" indicates that it produces both a text output and an image output.
This is the slower rendering mode, the image part produces one visual of the farm in png for each step together with a video aggregating all images. The 
text mode produces a text in the console. Finally, the monitored variables can be observed in tensorboard.

### Examples of tensor board display
Below is an example of the monitoring of the variables listed above, on four different runs. Here we consider the lille weather, and force no watering (0L of water).
<p align="center">
<img src="media/monitoring_lille_0L.png?raw=true" width="90%">
</p>
Tensor board enables to display the time series of all variables. You can see also some stochasticity, for instance in the second run (blue) the pollination did not go well, the fruits sayed small, and the plant also died early.
After the plant dies, it release its nutrients into the soil which can be seen in the soil curves.

### Examples of text rendering:


```python
Farm: Farm_Fields[Field-0[Weather-0(lille)_Soil-0(clay)_Plant-0(bean)_Pollinators-0(bee)]]_Farmers[BasicFarmer-0]
Short name: farm_1x1(lille_clay_bean_bee)
Fields:
	Field-0: {'latitude#°': 50.62, 'longitude#°': 3.05, 'altitude#m': 10} scale: 1.0m
		Shape:
			E
			
		Field-0-Entities:
			Weather-0:
			  year#int100: (range: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]; value: 0)
			  day#int365: (range: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364]; value: 0)
			  air_temperature: 
			    max#°C: (range: -100, 100; value: 22.0)
			    mean#°C: (range: -100, 100; value: 20.0)
			    min#°C: (range: -100, 100; value: 18.0)
			  humidity#%: (range: 0.0, 100.0; value: 50.0)
			  wind: 
			    speed#km.h-1: (range: 0.0, 500; value: 0.0)
			    direction: (range: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359]; value: 0)
			  clouds#%: (range: 0.0, 100.0; value: 0.0)
			  rain_amount#mm.day-1: (range: 0, 1000; value: 0)
			  consecutive_frost#day: (range: 0, 10000; value: 0)
			  consecutive_dry#day: (range: 0, 10000; value: 0)
			  forecast: 
			    air_temperature: 
			      mean#°C: [(range: -100, 100; value: 20.0),(range: -100, 100; value: 20.0),(range: -100, 100; value: 20.0),(range: -100, 100; value: 20.0),(range: -100, 100; value: 20.0)]
			      min#°C: [(range: -100, 100; value: 18.0),(range: -100, 100; value: 18.0),(range: -100, 100; value: 18.0),(range: -100, 100; value: 18.0),(range: -100, 100; value: 18.0)]
			      max#°C: [(range: -100, 100; value: 22.0),(range: -100, 100; value: 22.0),(range: -100, 100; value: 22.0),(range: -100, 100; value: 22.0),(range: -100, 100; value: 22.0)]
			    humidity#%: [(range: 0.0, 100.0; value: 50.0),(range: 0.0, 100.0; value: 50.0),(range: 0.0, 100.0; value: 50.0),(range: 0.0, 100.0; value: 50.0),(range: 0.0, 100.0; value: 50.0)]
			    clouds#%: [(range: 0.0, 100.0; value: 0.0),(range: 0.0, 100.0; value: 0.0),(range: 0.0, 100.0; value: 0.0),(range: 0.0, 100.0; value: 0.0),(range: 0.0, 100.0; value: 0.0)]
			    rain_amount#mm.day-1: [(range: 0.0, 100.0; value: 0.0),(range: 0.0, 100.0; value: 0.0),(range: 0.0, 100.0; value: 0.0),(range: 0.0, 100.0; value: 0.0),(range: 0.0, 100.0; value: 0.0)]
			    wind: 
			      speed#km.h-1: [(range: 0.0, 500; value: 0.0),(range: 0.0, 500; value: 0.0),(range: 0.0, 500; value: 0.0),(range: 0.0, 500; value: 0.0),(range: 0.0, 500; value: 0.0)]
			      direction: [(range: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359]; value: 0),(range: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359]; value: 0),(range: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359]; value: 0),(range: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359]; value: 0),(range: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359]; value: 0)]
	
			Soil-0:
			  available_N#g: [(range: 0, 10000; value: 100.0)]
			  available_P#g: [(range: 0, 10000; value: 100.0)]
			  available_K#g: [(range: 0, 100000; value: 100.0)]
			  available_C#g: [(range: 0, 100000; value: 100.0)]
			  available_Water#L: [(range: 0, 10000; value: 1.0)]
			  depth#m: [(range: 0, 10; value: 1.0)]
			  microlife_health_index#%: [(range: 0, 100; value: 75)]
			  amount_cide#g: 
			    pollinators: [(range: 0, 10000; value: 0)]
			    pests: [(range: 0, 10000; value: 0)]
			    soil: [(range: 0, 10000; value: 0)]
			    weeds: [(range: 0, 10000; value: 0)]
			  total_cumulated_added_water#L: (range: 0, 100000; value: 0)
			  total_cumulated_added_cide#g: 
			    pollinators: (range: 0, 100000; value: 0)
			    pests: (range: 0, 100000; value: 0)
			    soil: (range: 0, 100000; value: 0)
			    weeds: (range: 0, 100000; value: 0)
	
			Plant-0:
			  stage: [(range: ['none', 'seed', 'entered_grow', 'grow', 'entered_bloom', 'bloom', 'entered_fruit', 'fruit', 'entered_ripe', 'ripe', 'entered_seed', 'harvested', 'dead']; value: none)]
			  global_stage: (range: ['none', 'seed', 'entered_grow', 'grow', 'entered_bloom', 'bloom', 'entered_fruit', 'fruit', 'entered_ripe', 'ripe', 'entered_seed', 'harvested', 'dead', 'undefined']; value: none)
			  population#nb: [(range: 0, 100; value: 0)]
			  size#cm: [(range: 0, 1000; value: 0)]
			  flowers_per_plant#nb: [(range: 0, 1000; value: 0)]
			  pollinator_visits#nb: [(range: 0, 1000; value: 0)]
			  flowers_pollinated_per_plant#nb: [(range: 0, 1000; value: 0)]
			  fruits_per_plant#nb: [(range: 0, 1000; value: 0)]
			  fruit_weight#g: [(range: 0, 100000; value: 0)]
			  harvest_weight#kg: (range: 0, 1000000; value: 0)
			  age_seed#day: [(range: 0, 100; value: 0)]
			  consecutive_nogrow#day: [(range: 0, 100; value: 0)]
			  age_bloom#day: [(range: 0, 100; value: 0)]
			  consecutive_noweight#day: [(range: 0, 100; value: 0)]
			  age_ripe#day: [(range: 0, 100; value: 0)]
			  cumulated_nutrients_N#g: [(range: 0, 10000; value: 0)]
			  cumulated_nutrients_P#g: [(range: 0, 10000; value: 0)]
			  cumulated_nutrients_K#g: [(range: 0, 10000; value: 0)]
			  cumulated_nutrients_C#g: [(range: 0, 10000; value: 0)]
			  cumulated_stress_nutrients_N#g: [(range: 0, 10000; value: 0)]
			  cumulated_stress_nutrients_P#g: [(range: 0, 10000; value: 0)]
			  cumulated_stress_nutrients_K#g: [(range: 0, 10000; value: 0)]
			  cumulated_stress_nutrients_C#g: [(range: 0, 10000; value: 0)]
			  cumulated_stress_water#L: [(range: 0, 10000; value: 0)]
			  grow_size_threshold#cm: [(range: 0, 10000; value: 0)]
			  fruit_weight_threshold#g: [(range: 0, 100000; value: 0)]
	
			Pollinators-0:
			  occurrence#bin: [(range: ['True', 'False']; value: False)]
			  total_cumulated_occurrence#nb: (range: 0, 1000; value: 0)
	

Farmers:
	BasicFarmer-0:
		Field-0 Observation authorization: Y. Maximum observations per day: 2.
		Field-0 Intervention authorization: Y. Maximum interventions per day: 1.

Free farmgym observations:
	('Free', 'Field-0', 'Weather-0', 'day#int365', [])
	('Free', 'Field-0', 'Weather-0', 'air_temperature', [])
Available farmgym interventions:
	('BasicFarmer-0', 'Field-0', 'Soil-0', 'water_discrete', {'plot': ['(0, 0)'], 'amount#L': [0.0]})
Available gym actions: (as list [n1 n2 n3] where ni is one of the following)
-] Do nothing (empty).
0] Farmer BasicFarmer-0 performs intervention water_discrete with parameters {'plot': (0, 0), 'amount#L': 0.0} on Soil-0 in Field-0.

Initial step:
Farm:	farm_1x1(lille_clay_bean_bee)		Afternoon phase (interventions)
Actions planned: []
Observations received:
	- {'Free': {'Field-0': {'Weather-0': {'day#int365': 120}}}}
	- {'Free': {'Field-0': {'Weather-0': {'air_temperature': {'max#°C': [12.7], 'mean#°C': [7.4], 'min#°C': [0.8]}}}}}
Reward received: 0
Information:
	- intervention cost: 0

###################################
Farm:	farm_1x1(lille_clay_bean_bee)		Afternoon phase (interventions)
Actions planned: []
Observations received:
	- {'Free': {'Field-0': {'Weather-0': {'day#int365': 121}}}}
	- {'Free': {'Field-0': {'Weather-0': {'air_temperature': {'max#°C': [11.8], 'mean#°C': [7.7], 'min#°C': [2.2]}}}}}
Reward received: 0.0
Information:
	- intervention cost: 0

###################################
Farm:	farm_1x1(lille_clay_bean_bee)		Afternoon phase (interventions)
Actions planned: []
Observations received:
	- {'Free': {'Field-0': {'Weather-0': {'day#int365': 122}}}}
	- {'Free': {'Field-0': {'Weather-0': {'air_temperature': {'max#°C': [15.8], 'mean#°C': [9.7], 'min#°C': [2.8]}}}}}
Reward received: 0.0
Information:
	- intervention cost: 0

###################################
Farm:	farm_1x1(lille_clay_bean_bee)		Afternoon phase (interventions)
Actions planned: [0]
	- ('BasicFarmer-0', 'Field-0', 'Soil-0', 'water_discrete', {'plot': (0, 0), 'amount#L': 0.0})
Observations received:
	- {'Free': {'Field-0': {'Weather-0': {'day#int365': 123}}}}
	- {'Free': {'Field-0': {'Weather-0': {'air_temperature': {'max#°C': [13.8], 'mean#°C': [11.0], 'min#°C': [8.9]}}}}}
Reward received: 0.0
Information:
	- intervention cost: 1

###################################
Farm:	farm_1x1(lille_clay_bean_bee)		Afternoon phase (interventions)
Actions planned: []
Observations received:
	- {'Free': {'Field-0': {'Weather-0': {'day#int365': 124}}}}
	- {'Free': {'Field-0': {'Weather-0': {'air_temperature': {'max#°C': [12.7], 'mean#°C': [8.4], 'min#°C': [4.8]}}}}}
Reward received: 0.0
Information:
	- intervention cost: 0

###################################
Farm:	farm_1x1(lille_clay_bean_bee)		Afternoon phase (interventions)
Actions planned: [0]
	- ('BasicFarmer-0', 'Field-0', 'Soil-0', 'water_discrete', {'plot': (0, 0), 'amount#L': 0.0})
Observations received:
	- {'Free': {'Field-0': {'Weather-0': {'day#int365': 125}}}}
	- {'Free': {'Field-0': {'Weather-0': {'air_temperature': {'max#°C': [10.8], 'mean#°C': [7.0], 'min#°C': [3.1]}}}}}
Reward received: 0.0
Information:
	- intervention cost: 1

...

...


###################################
Farm:	farm_1x1(lille_clay_bean_bee)		Afternoon phase (interventions)
Actions planned: []
Observations received:
	- {'Free': {'Field-0': {'Weather-0': {'day#int365': 359}}}}
	- {'Free': {'Field-0': {'Weather-0': {'air_temperature': {'max#°C': [8.0], 'mean#°C': [5.6], 'min#°C': [2.1]}}}}}
Reward received: 0.0
Information:
	- intervention cost: 0

###################################
Stopping monitoring ...
Tensorflow is still listening on http://localhost:6006/, type 'exit' to close : exit
Closing writer ...
Farm:	farm_1x1(lille_clay_bean_bee)		Afternoon phase (interventions)
Actions planned: []
Observations received:
	- {'Free': {'Field-0': {'Weather-0': {'day#int365': 360}}}}
	- {'Free': {'Field-0': {'Weather-0': {'air_temperature': {'max#°C': [9.8], 'mean#°C': [8.4], 'min#°C': [6.2]}}}}}
Reward received: 0.0
Information:
	- intervention cost: 0
Terminated.
```
At the end of a rendering with an image option, one should type exit to properly exit the tensorboard, otherwise the video will not be genetated (only the images).

### Example of image and video rendering

<p align="center">
<video id="Farm rendering" width="640" height="360" controls>
												<source src="media/farm_low.mp4" type="video/mp4">
												Your browser does not support the video tag.
</video>
</p>

<p align="center">
The simulation starts with seeds at day 120. Later, the plant slowly grows, and reaches its first flowers, here on day 208.
<br>
<img src="media/farm-day-120.png?raw=true" width="24%">
<img src="media/farm-day-146.png?raw=true" width="24%">
<img src="media/farm-day-184.png?raw=true" width="24%">
<img src="media/farm-day-208.png?raw=true" width="24%"><br>
A bit later some pollinators come visit the plant, which enables to start fruits, which grow over time. Not that the speed at which the plabt grows is not necessarily realistic, here it tends to be slower than real beans.
<br>
<img src="media/farm-day-211.png?raw=true" width="24%">
<img src="media/farm-day-212.png?raw=true" width="24%">
<img src="media/farm-day-222.png?raw=true" width="24%">
<img src="media/farm-day-250.png?raw=true" width="24%">
<br>
Eventually, the fruits become ripe  can can be harvested. Here, no harvest is done, so after a while all the fruit rotten, and we consider at this stage that the plant dies. 
Here we continue the simulation long later, the dead plant has been reabsorbed by the soil and we see on Day 355 the first frost event.
<br>
<img src="media/farm-day-263.png?raw=true" width="24%">
<img src="media/farm-day-268.png?raw=true" width="24%">
<img src="media/farm-day-275.png?raw=true" width="24%">
<img src="media/farm-day-355.png?raw=true" width="24%">
</p>


## Weather interpolation

We can define different weathers, for instance, a typical weather in Lille, in Montpellier, 
a purely constant Rainy weather and a purely constant Dry weather.
We can then interpolate between them to create novel weathers. 
For instance,  in the file weather_specificatoin.yaml, we can specify a 70%-30% mix between Lille and Rainy weather as follows
```yaml
lille2:
  ...
  one_year_data_filename:
    weather_data/lille.csv: 0.7
    weather_data/constant_rain.csv: 0.3
 ...
```
Such a weather will have more rainy, cloudy and humid days than the typical Lille weather.
Similarly, we can define lille3 to be a 40%-60% mix between Lille and Rainy weather,
or montpellier2 to be a 70%-30% mix between Montpellier and Dry weather, having more sunny, dry, and hot weather than the typical Montpellier weather.

The following two images show respectively a comparison of the weather lille, lille2 and lille3,
and a comparison of the weather montpellier, montpellier2 and montpellier3,
<p align="center">
<img src="media/Weather_Lille_Lille2_Lille3.png?raw=true" width="95%"><br>
<img src="media/Weather_Montpellier_Montpellier2_Montpellier3.png?raw=true" width="95%">
</p>
