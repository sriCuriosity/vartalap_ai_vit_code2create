"""
Sales Forecasting Model using LSTM and Prophet
Dataset: Historical sales data from the business
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from prophet import Prophet
import sqlite3
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SalesForecastingModel:
    def __init__(self, db_path, lookback_window=30):
        self.db_path = db_path
        self.lookback_window = lookback_window
        self.scaler = MinMaxScaler()
        self.lstm_model = None
        self.prophet_model = None
        
    def load_sales_data(self):
        """Load sales data from database"""
        with sqlite3.connect(self.db_path) as conn:
            # Get daily sales data
            query = """
            SELECT date, SUM(total_amount) as daily_sales
            FROM bills 
            WHERE transaction_type = 'Debit'
            GROUP BY date
            ORDER BY date
            """
            
            df = pd.read_sql_query(query, conn)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # Fill missing dates with 0
            df = df.resample('D').sum().fillna(0)
            
            return df
    
    def load_product_sales_data(self):
        """Load product-wise sales data"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
            SELECT date, items
            FROM bills 
            WHERE transaction_type = 'Debit'
            ORDER BY date
            """
            
            df = pd.read_sql_query(query, conn)
            df['date'] = pd.to_datetime(df['date'])
            
            # Parse items and create product-wise sales
            product_sales = {}
            
            for _, row in df.iterrows():
                try:
                    items = json.loads(row['items'])
                    for item in items:
                        product = item.get('name', '')
                        quantity = item.get('quantity', 0)
                        amount = item.get('total', 0)
                        
                        if product not in product_sales:
                            product_sales[product] = []
                        
                        product_sales[product].append({
                            'date': row['date'],
                            'quantity': quantity,
                            'amount': amount
                        })
                except:
                    continue
            
            return product_sales
    
    def prepare_lstm_data(self, data, target_col='daily_sales'):
        """Prepare data for LSTM model"""
        # Scale the data
        scaled_data = self.scaler.fit_transform(data[[target_col]])
        
        X, y = [], []
        
        for i in range(self.lookback_window, len(scaled_data)):
            X.append(scaled_data[i-self.lookback_window:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        return X, y
    
    def build_lstm_model(self, input_shape):
        """Build LSTM model for sales forecasting"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model
    
    def train_lstm_model(self, data, epochs=100, batch_size=32):
        """Train LSTM model"""
        X, y = self.prepare_lstm_data(data)
        
        # Split data
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Build model
        self.lstm_model = self.build_lstm_model((X_train.shape[1], 1))
        
        # Train model
        history = self.lstm_model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            verbose=1
        )
        
        # Evaluate
        train_pred = self.lstm_model.predict(X_train)
        test_pred = self.lstm_model.predict(X_test)
        
        # Inverse transform predictions
        train_pred = self.scaler.inverse_transform(train_pred)
        test_pred = self.scaler.inverse_transform(test_pred)
        y_train_actual = self.scaler.inverse_transform(y_train.reshape(-1, 1))
        y_test_actual = self.scaler.inverse_transform(y_test.reshape(-1, 1))
        
        # Calculate metrics
        train_mae = mean_absolute_error(y_train_actual, train_pred)
        test_mae = mean_absolute_error(y_test_actual, test_pred)
        
        print(f"LSTM Model - Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
        
        return history
    
    def train_prophet_model(self, data):
        """Train Prophet model"""
        # Prepare data for Prophet
        prophet_data = data.reset_index()
        prophet_data.columns = ['ds', 'y']
        
        # Initialize and fit Prophet model
        self.prophet_model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05
        )
        
        self.prophet_model.fit(prophet_data)
        
        # Make predictions on historical data for evaluation
        forecast = self.prophet_model.predict(prophet_data)
        
        # Calculate metrics
        mae = mean_absolute_error(prophet_data['y'], forecast['yhat'])
        print(f"Prophet Model - MAE: {mae:.2f}")
        
        return forecast
    
    def forecast_lstm(self, data, days_ahead=30):
        """Forecast using LSTM model"""
        if self.lstm_model is None:
            raise ValueError("LSTM model not trained yet")
        
        # Get last lookback_window days
        last_data = data['daily_sales'].values[-self.lookback_window:]
        last_data_scaled = self.scaler.transform(last_data.reshape(-1, 1))
        
        predictions = []
        current_batch = last_data_scaled.reshape((1, self.lookback_window, 1))
        
        for _ in range(days_ahead):
            # Predict next day
            pred = self.lstm_model.predict(current_batch)[0]
            predictions.append(pred)
            
            # Update batch for next prediction
            current_batch = np.append(current_batch[:, 1:, :], [[pred]], axis=1)
        
        # Inverse transform predictions
        predictions = self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        
        # Create forecast dataframe
        last_date = data.index[-1]
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead)
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_sales': predictions.flatten()
        })
        
        return forecast_df
    
    def forecast_prophet(self, days_ahead=30):
        """Forecast using Prophet model"""
        if self.prophet_model is None:
            raise ValueError("Prophet model not trained yet")
        
        # Create future dataframe
        future = self.prophet_model.make_future_dataframe(periods=days_ahead)
        
        # Make forecast
        forecast = self.prophet_model.predict(future)
        
        # Return only future predictions
        future_forecast = forecast.tail(days_ahead)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        future_forecast.columns = ['date', 'predicted_sales', 'lower_bound', 'upper_bound']
        
        return future_forecast
    
    def ensemble_forecast(self, data, days_ahead=30):
        """Combine LSTM and Prophet forecasts"""
        lstm_forecast = self.forecast_lstm(data, days_ahead)
        prophet_forecast = self.forecast_prophet(days_ahead)
        
        # Combine predictions (weighted average)
        ensemble_forecast = pd.DataFrame({
            'date': lstm_forecast['date'],
            'lstm_prediction': lstm_forecast['predicted_sales'],
            'prophet_prediction': prophet_forecast['predicted_sales'],
            'ensemble_prediction': (lstm_forecast['predicted_sales'] * 0.6 + 
                                  prophet_forecast['predicted_sales'] * 0.4),
            'lower_bound': prophet_forecast['lower_bound'],
            'upper_bound': prophet_forecast['upper_bound']
        })
        
        return ensemble_forecast
    
    def analyze_product_trends(self):
        """Analyze product-wise sales trends"""
        product_sales = self.load_product_sales_data()
        
        trends = {}
        
        for product, sales_data in product_sales.items():
            if len(sales_data) < 10:  # Skip products with insufficient data
                continue
            
            df = pd.DataFrame(sales_data)
            df = df.groupby('date').agg({
                'quantity': 'sum',
                'amount': 'sum'
            }).reset_index()
            
            # Calculate trend
            if len(df) > 1:
                recent_avg = df.tail(7)['amount'].mean()
                older_avg = df.head(7)['amount'].mean()
                
                if older_avg > 0:
                    trend_pct = ((recent_avg - older_avg) / older_avg) * 100
                else:
                    trend_pct = 0
                
                trends[product] = {
                    'total_sales': df['amount'].sum(),
                    'total_quantity': df['quantity'].sum(),
                    'trend_percentage': trend_pct,
                    'avg_daily_sales': df['amount'].mean(),
                    'days_with_sales': len(df)
                }
        
        # Sort by total sales
        sorted_trends = dict(sorted(trends.items(), key=lambda x: x[1]['total_sales'], reverse=True))
        
        return sorted_trends
    
    def generate_insights(self, forecast_data, product_trends):
        """Generate business insights"""
        insights = {
            'forecast_summary': {
                'next_week_sales': forecast_data.head(7)['ensemble_prediction'].sum(),
                'next_month_sales': forecast_data['ensemble_prediction'].sum(),
                'growth_trend': 'increasing' if forecast_data['ensemble_prediction'].iloc[-1] > forecast_data['ensemble_prediction'].iloc[0] else 'decreasing'
            },
            'top_products': list(product_trends.keys())[:5],
            'growing_products': [
                product for product, data in product_trends.items() 
                if data['trend_percentage'] > 10
            ],
            'declining_products': [
                product for product, data in product_trends.items() 
                if data['trend_percentage'] < -10
            ],
            'recommendations': []
        }
        
        # Generate recommendations
        if insights['forecast_summary']['growth_trend'] == 'increasing':
            insights['recommendations'].append("Sales are trending upward. Consider increasing inventory for top products.")
        else:
            insights['recommendations'].append("Sales are declining. Focus on customer retention and promotional activities.")
        
        if insights['growing_products']:
            insights['recommendations'].append(f"Products showing growth: {', '.join(insights['growing_products'][:3])}. Consider promoting these items.")
        
        if insights['declining_products']:
            insights['recommendations'].append(f"Products declining: {', '.join(insights['declining_products'][:3])}. Review pricing and marketing strategy.")
        
        return insights
    
    def plot_forecast(self, data, forecast_data):
        """Plot historical data and forecast"""
        plt.figure(figsize=(15, 8))
        
        # Plot historical data
        plt.plot(data.index, data['daily_sales'], label='Historical Sales', color='blue')
        
        # Plot forecast
        plt.plot(forecast_data['date'], forecast_data['ensemble_prediction'], 
                label='Forecast', color='red', linestyle='--')
        
        # Plot confidence interval
        plt.fill_between(forecast_data['date'], 
                        forecast_data['lower_bound'], 
                        forecast_data['upper_bound'], 
                        alpha=0.3, color='red')
        
        plt.title('Sales Forecast')
        plt.xlabel('Date')
        plt.ylabel('Sales Amount (₹)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# Training and usage script
if __name__ == "__main__":
    # Initialize forecasting model
    db_path = "path/to/bills.db"
    forecaster = SalesForecastingModel(db_path)
    
    # Load data
    sales_data = forecaster.load_sales_data()
    
    if len(sales_data) > 60:  # Need sufficient data for training
        # Train models
        print("Training LSTM model...")
        forecaster.train_lstm_model(sales_data)
        
        print("Training Prophet model...")
        forecaster.train_prophet_model(sales_data)
        
        # Generate forecasts
        print("Generating forecasts...")
        forecast = forecaster.ensemble_forecast(sales_data, days_ahead=30)
        
        # Analyze product trends
        product_trends = forecaster.analyze_product_trends()
        
        # Generate insights
        insights = forecaster.generate_insights(forecast, product_trends)
        
        # Display results
        print("\n=== SALES FORECAST ===")
        print(f"Next week sales: ₹{insights['forecast_summary']['next_week_sales']:.2f}")
        print(f"Next month sales: ₹{insights['forecast_summary']['next_month_sales']:.2f}")
        print(f"Trend: {insights['forecast_summary']['growth_trend']}")
        
        print("\n=== TOP PRODUCTS ===")
        for product in insights['top_products']:
            print(f"- {product}")
        
        print("\n=== RECOMMENDATIONS ===")
        for rec in insights['recommendations']:
            print(f"• {rec}")
        
        # Plot forecast
        forecaster.plot_forecast(sales_data, forecast)
        
    else:
        print("Insufficient data for training. Need at least 60 days of sales data.")
    
    print("Sales Forecasting Model Ready!")