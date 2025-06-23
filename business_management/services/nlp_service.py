import re
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import sqlite3
import os

class BusinessNLPService:
    """Natural Language Processing service for business queries"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.intent_patterns = self.load_intent_patterns()
        self.response_templates = self.load_response_templates()
    
    def load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent recognition patterns"""
        return {
            "sales_query": [
                r"(?:sales|revenue|income|earnings?|turnover)",
                r"(?:how much|total|amount).*(?:sold|earned|made)",
                r"(?:profit|loss|margin)",
                r"(?:performance|growth|trend)"
            ],
            "customer_query": [
                r"(?:customer|client|buyer)s?",
                r"(?:who|which).*(?:customer|client)",
                r"(?:top|best|frequent).*(?:customer|buyer)",
                r"(?:customer.*(?:analysis|behavior|pattern))"
            ],
            "inventory_query": [
                r"(?:inventory|stock|product)s?",
                r"(?:how many|quantity|amount).*(?:stock|inventory)",
                r"(?:out of stock|low stock|shortage)",
                r"(?:product.*(?:list|catalog|available))"
            ],
            "date_query": [
                r"(?:today|yesterday|this week|last week|this month|last month)",
                r"(?:from|between|since).*(?:to|until)",
                r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",
                r"(?:january|february|march|april|may|june|july|august|september|october|november|december)"
            ],
            "translation_request": [
                r"(?:translate|translation)",
                r"(?:tamil|english).*(?:to|into).*(?:tamil|english)",
                r"(?:what.*(?:tamil|english))",
                r"(?:meaning|means).*(?:tamil|english)"
            ],
            "help_request": [
                r"(?:help|assist|guide|how)",
                r"(?:what.*(?:can|do|features))",
                r"(?:explain|show|tell).*(?:how|what)",
                r"(?:tutorial|instructions|manual)"
            ]
        }
    
    def load_response_templates(self) -> Dict[str, List[str]]:
        """Load response templates for different intents"""
        return {
            "sales_query": [
                "Based on your sales data, {analysis}",
                "Your sales performance shows {trend}",
                "Revenue analysis indicates {insight}"
            ],
            "customer_query": [
                "Customer analysis reveals {insight}",
                "Your customer base shows {pattern}",
                "Top customers include {customers}"
            ],
            "inventory_query": [
                "Your inventory status: {status}",
                "Product analysis shows {insight}",
                "Stock levels indicate {information}"
            ],
            "general": [
                "I can help you with {capabilities}",
                "Here's what I found: {information}",
                "Based on your data: {analysis}"
            ]
        }
    
    def classify_intent(self, query: str) -> str:
        """Classify user query intent"""
        query_lower = query.lower()
        
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            intent_scores[intent] = score
        
        # Return intent with highest score
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            if intent_scores[best_intent] > 0:
                return best_intent
        
        return "general"
    
    def extract_entities(self, query: str) -> Dict:
        """Extract entities from user query"""
        entities = {
            "dates": [],
            "customers": [],
            "products": [],
            "amounts": [],
            "time_periods": []
        }
        
        # Extract dates
        date_patterns = [
            r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}",
            r"(?:today|yesterday|tomorrow)",
            r"(?:this|last|next)\s+(?:week|month|year)",
            r"(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:,\s*\d{4})?"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["dates"].extend(matches)
        
        # Extract amounts
        amount_patterns = [
            r"₹\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*rupees?",
            r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*rs\.?"
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["amounts"].extend(matches)
        
        # Extract customer references
        customer_patterns = [
            r"customer\s+([A-Z])",
            r"client\s+([A-Z])",
            r"([A-Z])\s+customer"
        ]
        
        for pattern in customer_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["customers"].extend(matches)
        
        return entities
    
    def analyze_sales_data(self, entities: Dict) -> Dict:
        """Analyze sales data based on extracted entities"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Default to last 30 days if no date specified
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
                # Get total sales
                cursor.execute('''
                    SELECT SUM(total_amount) FROM bills 
                    WHERE date BETWEEN ? AND ? AND transaction_type = 'Debit'
                ''', (start_date, end_date))
                
                total_sales = cursor.fetchone()[0] or 0
                
                # Get transaction count
                cursor.execute('''
                    SELECT COUNT(*) FROM bills 
                    WHERE date BETWEEN ? AND ? AND transaction_type = 'Debit'
                ''', (start_date, end_date))
                
                transaction_count = cursor.fetchone()[0] or 0
                
                # Get top products
                cursor.execute('''
                    SELECT items FROM bills 
                    WHERE date BETWEEN ? AND ? AND transaction_type = 'Debit'
                ''', (start_date, end_date))
                
                all_items = []
                for row in cursor.fetchall():
                    try:
                        items = json.loads(row[0])
                        all_items.extend(items)
                    except:
                        continue
                
                # Count product frequencies
                product_counts = {}
                for item in all_items:
                    name = item.get('name', '')
                    if name:
                        product_counts[name] = product_counts.get(name, 0) + item.get('quantity', 0)
                
                top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                return {
                    "total_sales": total_sales,
                    "transaction_count": transaction_count,
                    "average_transaction": total_sales / transaction_count if transaction_count > 0 else 0,
                    "top_products": top_products,
                    "period": f"{start_date} to {end_date}"
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_customer_data(self, entities: Dict) -> Dict:
        """Analyze customer data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get customer transaction summary
                cursor.execute('''
                    SELECT customer_key, COUNT(*) as transaction_count, 
                           SUM(total_amount) as total_amount
                    FROM bills 
                    WHERE transaction_type = 'Debit'
                    GROUP BY customer_key
                    ORDER BY total_amount DESC
                ''')
                
                customers = []
                for row in cursor.fetchall():
                    customers.append({
                        "customer": row[0],
                        "transactions": row[1],
                        "total_amount": row[2]
                    })
                
                return {
                    "customer_count": len(customers),
                    "customers": customers,
                    "top_customer": customers[0] if customers else None
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_inventory_data(self, entities: Dict) -> Dict:
        """Analyze inventory/product data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get product list
                cursor.execute('SELECT name FROM products ORDER BY name')
                products = [row[0] for row in cursor.fetchall()]
                
                # Get recent sales data for products
                cursor.execute('''
                    SELECT items FROM bills 
                    WHERE transaction_type = 'Debit' 
                    AND date >= date('now', '-30 days')
                ''')
                
                recent_sales = {}
                for row in cursor.fetchall():
                    try:
                        items = json.loads(row[0])
                        for item in items:
                            name = item.get('name', '')
                            if name:
                                recent_sales[name] = recent_sales.get(name, 0) + item.get('quantity', 0)
                    except:
                        continue
                
                # Identify fast and slow moving products
                fast_moving = sorted(recent_sales.items(), key=lambda x: x[1], reverse=True)[:10]
                
                return {
                    "total_products": len(products),
                    "fast_moving": fast_moving,
                    "recent_sales_summary": recent_sales
                }
                
        except Exception as e:
            return {"error": str(e)}
    
    def generate_response(self, query: str) -> str:
        """Generate intelligent response to user query"""
        # Classify intent
        intent = self.classify_intent(query)
        
        # Extract entities
        entities = self.extract_entities(query)
        
        # Generate response based on intent
        if intent == "sales_query":
            data = self.analyze_sales_data(entities)
            return self.format_sales_response(data)
        
        elif intent == "customer_query":
            data = self.analyze_customer_data(entities)
            return self.format_customer_response(data)
        
        elif intent == "inventory_query":
            data = self.analyze_inventory_data(entities)
            return self.format_inventory_response(data)
        
        elif intent == "translation_request":
            return self.format_translation_response(query)
        
        elif intent == "help_request":
            return self.format_help_response()
        
        else:
            return self.format_general_response(query)
    
    def format_sales_response(self, data: Dict) -> str:
        """Format sales analysis response"""
        if "error" in data:
            return f"I encountered an error analyzing your sales data: {data['error']}"
        
        response = f"""📊 **Sales Analysis** ({data['period']})

💰 **Total Sales**: ₹{data['total_sales']:,.2f}
📝 **Transactions**: {data['transaction_count']}
📈 **Average per Transaction**: ₹{data['average_transaction']:,.2f}

🏆 **Top Products**:"""
        
        for i, (product, quantity) in enumerate(data['top_products'][:3], 1):
            response += f"\n{i}. {product} ({quantity} units)"
        
        response += "\n\n💡 **Insights**: Your traditional grain products are performing well. Consider promoting seasonal items for better sales."
        
        return response
    
    def format_customer_response(self, data: Dict) -> str:
        """Format customer analysis response"""
        if "error" in data:
            return f"I encountered an error analyzing customer data: {data['error']}"
        
        response = f"""👥 **Customer Analysis**

📊 **Total Customers**: {data['customer_count']}"""
        
        if data['top_customer']:
            top = data['top_customer']
            response += f"""

🥇 **Top Customer**: {top['customer']}
   • Transactions: {top['transactions']}
   • Total Value: ₹{top['total_amount']:,.2f}"""
        
        response += "\n\n💡 **Recommendation**: Focus on customer retention strategies and consider loyalty programs for your top customers."
        
        return response
    
    def format_inventory_response(self, data: Dict) -> str:
        """Format inventory analysis response"""
        if "error" in data:
            return f"I encountered an error analyzing inventory data: {data['error']}"
        
        response = f"""📦 **Inventory Analysis**

📋 **Total Products**: {data['total_products']}

🔥 **Fast Moving Items** (Last 30 days):"""
        
        for i, (product, quantity) in enumerate(data['fast_moving'][:5], 1):
            response += f"\n{i}. {product} ({quantity} units sold)"
        
        response += "\n\n💡 **Tip**: Monitor stock levels for fast-moving items and consider bulk purchasing for better margins."
        
        return response
    
    def format_translation_response(self, query: str) -> str:
        """Format translation help response"""
        return """🌐 **Translation Help**

I can help translate between Tamil and English for your business needs:

**Common Translations**:
• நாட்டு சக்கரை ↔ Country sugar
• ராகி மாவு ↔ Ragi flour
• கம்பு ↔ Pearl millet
• வாடிக்கையாளர் ↔ Customer

Just type the text you want to translate, and I'll provide the translation along with context!"""
    
    def format_help_response(self) -> str:
        """Format help response"""
        return """🤖 **AI Assistant Help**

I can help you with:

🔍 **Analysis & Insights**
• "Show me sales trends"
• "Who are my top customers?"
• "What products are selling well?"

📊 **Data Queries**
• "Sales for last month"
• "Customer A transactions"
• "Inventory status"

🌐 **Translation**
• "Translate நாட்டு சக்கரை to English"
• "What is Country sugar in Tamil?"

💡 **Smart Suggestions**
• Business optimization tips
• Customer retention strategies
• Inventory management advice

Just ask me anything about your business in natural language!"""
    
    def format_general_response(self, query: str) -> str:
        """Format general response"""
        return f"""I understand you're asking about: "{query}"

I can help you with:
• Sales analysis and trends
• Customer insights and behavior
• Inventory management
• Tamil-English translation
• Business optimization tips

Could you be more specific about what information you need? For example:
- "Show me sales for this month"
- "Who is my best customer?"
- "What products should I stock more of?"
"""