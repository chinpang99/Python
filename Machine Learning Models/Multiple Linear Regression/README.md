# Multiple Linear Regression:

- Equation: y = c + m0x0 + m1x1 + .... mIxI. 
- If the data contains categorical variable, we should use dummy variable (by creating 1 column for each categorical indicator and use binary indicator to indicate the result)
- Equation (contains categorical features): c + m0x0 + m1x1 + m2D2 .... mIxI. (the number of D must be -1. For exp: If there's 6 dummy variable columns, we can only include 5 dummy variable column in our equation).


5 Methods of building a good models:
1. All-in [Throw all variables]
   - Might know all variables is useful in constructing the models OR
   - You have to all these variables OR
   - Preparing for Backward Elminination

2. Backward Elimination 
   
   Step 1: Select the significantl level to stay in the model
   
   Step 2: Fit the full model with all possible predictors
   
   Step 3: Consider the predictor with the highest P-value. If P-value is significant than significance value. Proceed to step 4
   
   Step 4: Remove the predictor
   
   Step 5: Fit model without this variable* => It might need to rebuild the whole model after remove the variables. After removed then back to step 3 onwards. 

3. Forward Selection
  
   Step 1: Select a significance level to enter the model 
  
   Step 2: Fit all simple regression models. Select the one with the lowest P-value
  
   Step 3: Keep this variable and fit all possible models with 1 extra predictor added to the one(s) you already have.
  
   Step 4: Consider the predictor with the lowest P-value. If P<SL then go to step 3 until the variable's P-value is > SL, then stop. 

4. Bidirectional Elimination [also known as Stepwise Regression]
  
   Step 1: Select a significance level to enter and to stay in the model. 
  
   Step 2: Perform the next step of Forward selection (new variables must have P-value < SL to enter)
  
   Step 3: Perform all steps of Backward selection (old variables must have P-value < SL to stay)
  
   Step 4: No new variables can enter and exit. The model is ready. 
