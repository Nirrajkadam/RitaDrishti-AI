-- RitaDrishti-AI — Initial Seed Data Script

INSERT INTO companies (company_id, name, domain, industry, description, verified_status, country_code)
VALUES 
('11111111-1111-1111-1111-111111111111', 'Acme Cloud Solutions', 'acmecloud.io', 'Cloud Software', 'Enterprise SaaS provider offering cloud infrastructure & AI middleware.', TRUE, 'US'),
('22222222-2222-2222-2222-222222222222', 'FinPay Tech', 'finpay.com', 'Fintech', 'Digital payment gateway and mobile wallet service for e-commerce.', TRUE, 'US'),
('33333333-3333-3333-3333-333333333333', 'Apex Logistics', 'apexlogistics.net', 'Logistics & Supply Chain', 'Global freight forwarding, parcel delivery, and inventory management.', FALSE, 'IN')
ON CONFLICT (domain) DO NOTHING;

INSERT INTO trust_scores (score_id, company_id, trust_index, transparency_score, sentiment_factor, fake_review_penalty, complaint_penalty, trust_tier)
VALUES
(uuid_generate_v4(), '11111111-1111-1111-1111-111111111111', 88.50, 92.00, 85.00, 2.50, 4.00, 'High Trust'),
(uuid_generate_v4(), '22222222-2222-2222-2222-222222222222', 64.20, 70.00, 58.00, 12.00, 15.00, 'Moderate Trust'),
(uuid_generate_v4(), '33333333-3333-3333-3333-333333333333', 38.10, 42.00, 35.00, 28.00, 32.00, 'Critical Alert');

INSERT INTO risk_scores (risk_id, company_id, overall_risk_score, fraud_risk, regulatory_risk, reputational_risk, risk_level, anomaly_signals)
VALUES
(uuid_generate_v4(), '11111111-1111-1111-1111-111111111111', 12.40, 5.00, 10.00, 15.00, 'Low', '["Stable review frequency", "High resolution rate"]'),
(uuid_generate_v4(), '22222222-2222-2222-2222-222222222222', 45.80, 40.00, 55.00, 42.00, 'Medium', '["Unusual spike in 5-star reviews", "Unresolved payment complaints"]'),
(uuid_generate_v4(), '33333333-3333-3333-3333-333333333333', 82.30, 88.00, 75.00, 84.00, 'Severe', '["High probability fake review cluster", "Unresolved loss of shipment claims"]');

INSERT INTO reviews (review_id, company_id, source, rating, raw_text, cleaned_text, reviewer_name, review_date)
VALUES
(uuid_generate_v4(), '11111111-1111-1111-1111-111111111111', 'Trustpilot', 5.00, 'Outstanding cloud uptime and superb customer support! Highly recommended for enterprise workloads.', 'outstanding cloud uptime superb customer support highly recommended enterprise workloads', 'Sarah Jenkins', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(uuid_generate_v4(), '22222222-2222-2222-2222-222222222222', 'Google', 1.00, 'Payment failed twice and customer support hasn refund my money after 3 weeks. Avoid this service!', 'payment failed twice customer support havent refunded money 3 weeks avoid service', 'David Miller', CURRENT_TIMESTAMP - INTERVAL '5 days'),
(uuid_generate_v4(), '33333333-3333-3333-3333-333333333333', 'ConsumerAffairs', 1.00, 'Parcel went missing! They refuse to respond to emails and phone numbers are disconnected.', 'parcel went missing refuse respond emails phone numbers disconnected', 'Rajesh Kumar', CURRENT_TIMESTAMP - INTERVAL '1 day');
