#!/usr/bin/env python3
"""Bayesian Belief Update Calculator"""
import sys

def bayesian_update(prior, true_positive, false_positive):
    prior_odds = prior / (1 - prior)
    likelihood_ratio = true_positive / false_positive if false_positive > 0 else 999
    posterior_odds = prior_odds * likelihood_ratio
    posterior = posterior_odds / (1 + posterior_odds)
    return posterior, likelihood_ratio

def main():
    if len(sys.argv) < 4:
        print("Usage: python belief_update.py [prior%] [P(E|H)%] [P(E|~H)%]")
        print("\nExample: python belief_update.py 15 80 40")
        return
    
    prior = float(sys.argv[1]) / 100
    true_pos = float(sys.argv[2]) / 100
    false_pos = float(sys.argv[3]) / 100
    
    posterior, bf = bayesian_update(prior, true_pos, false_pos)
    
    print(f"\n=== Bayesian Update ===")
    print(f"Prior: {prior*100:.1f}%")
    print(f"P(E|H): {true_pos*100:.1f}%")
    print(f"P(E|~H): {false_pos*100:.1f}%")
    print(f"Bayes Factor: {bf:.2f}")
    print(f"→ Posterior: {posterior*100:.1f}%")
    
    if posterior > 0.7: print(f"\n[DECISION] Proceed (>70%)")
    elif posterior < 0.3: print(f"\n[DECISION] Kill (<30%)")
    else: print(f"\n[DECISION] Gather more data (30-70%)")

if __name__ == "__main__":
    main()
