Feature: As a user, I can calculate the sum of two numbers
 
Background:
  Given I have a calculator
  And I have some fingers
 
 
@id:1 @fast
Scenario Outline: Cucumber Test As a user, I can calculate the sum of two positive numbers
  Given I have entered <input_1> into the calculator
  And I have entered <input_2> into the calculator
  When I press <button>
  Then the result should be <output> on the screen
 
Examples:
| input_1   | input_2   | button| output|
| 20        | 30        | add   | 50    |
| 2         | 5         | add   | 7     |
| 0         | 40        | add   | 40    |
| 4         | 50        | add   | 54    |
| 5         | 50        | add   | 55    |
 
 
@id:2
Scenario: Cucumber Test As a user, I can calculate the sum of two negative numbers
  Given I have entered -1 into the calculator
  And I have entered -3 into the calculator
  When I press add
  Then the result should be -4 on the screen