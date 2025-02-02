
import pandas as pd
import numpy as np
import mlflow
from mlflow.models import infer_signature
from modelos import xgb
from evaluaciones import evaluaciones
df=pd.read_csv("D:\Documentos\Github\Prueba_tecnica_Azzorti\Datosmodelo.csv")
# Define the model hyperparameters
params = {
        "objective": "reg:squarederror",  # Para regresión con MSE
        "learning_rate": 0.05,
        "n_estimators": 600,
        "max_depth": 5,
        "min_child_weight": 1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "eval_metric": "rmse",  # Métrica de evaluación durante el entrenamiento
        "random_state": 8888,
    }
modelo,X_train, X_test, y_train, y_test,X,y=xgb(df,params)
# Predict on the test set
y_pred = modelo.predict(X_test)

# Calculate metrics
cv_scores,cv_rmse,mae,rmse,r2=evaluaciones(modelo,X,y,y_pred,y_test)
stddatos=df["VENTA"].std()                                
#mlflow.set_tracking_uri(uri="http://locashost:5000")
mlflow.set_tracking_uri(uri="http://127.0.0.1:5000")
# Create a new MLflow Experiment
mlflow.set_experiment("MLflow Quickstart")

# Start an MLflow run
with mlflow.start_run():
    # Log the hyperparameters
    mlflow.log_params(params)

    # Log the loss metric
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("r2",r2)
    mlflow.log_metric("std_target",stddatos)
    mlflow.log_metric("cv_score", -np.mean(cv_scores))
    mlflow.log_metric("cv_rmse", -np.mean(cv_rmse))
    #for i, score in enumerate(cv_rmse):
       # mlflow.log_metric(f"cv_score_fold_{i}", score)


    # Set a tag that we can use to remind ourselves what this run was for
    mlflow.set_tag("First run XGBOOST", "First parameters")

    # Infer the model signature
    signature = infer_signature(X_train, modelo.predict(X_train))

    # Log the model
    model_info = mlflow.sklearn.log_model(
        sk_model=modelo,
        artifact_path="modelo_ventas",
        signature=signature,
        input_example=X_train,
        registered_model_name="tracking-xgboost",
    )
# Load the model back for predictions as a generic Python Function model
loaded_model = mlflow.pyfunc.load_model(model_info.model_uri)

predictions = loaded_model.predict(X_test)

feature_names = df.columns

result = pd.DataFrame(X_test, columns=feature_names)
result["actual_class"] = y_test
result["predicted_class"] = predictions

result[:4]

