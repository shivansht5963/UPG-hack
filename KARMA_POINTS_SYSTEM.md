# Karma Points System - CircuTrade AI

## The Concept: "Gamified Reputation System"
Karma points reward users for positive actions in the circular economy. Higher karma = Better reputation & more trust!

## How Karma is Given

### Current Implementation
**Range:** 0 - 1000 points

### Karma Actions (Currently Implemented)

#### For Generators (Waste Sellers):
- ✅ **Create Listing**: +5 karma
  - Reason: "Created new waste listing"
  - Location: `marketplace/views.py` - `create_listing()`
  
#### For Buyers:
- 🔜 Complete Purchase: +10 karma (to be implemented)
- 🔜 Leave Review: +3 karma (to be implemented)

### Karma Deductions (Suggested - Not Yet Implemented)
- ❌ **Cancel Order**: -5 karma
- ❌ **Late Delivery**: -10 karma
- ❌ **Fake Listing**: -50 karma
- ❌ **Low Trust Score**: -5 karma (if verified trust < 30%)

## Technical Implementation

### The Method
```python
def update_karma(self, points, reason=""):
    """
    Update karma score with validation
    :param points: Points to add (positive) or subtract (negative)
    :param reason: Optional reason for karma change
    """
    new_score = self.karma_score + points
    self.karma_score = max(0, min(1000, new_score))  # Clamp between 0-1000
    self.save()
    
    # Log karma change
    print(f"Karma updated for {self.username}: {points:+d} points. Reason: {reason}")
    
    return self.karma_score
```

### Usage Example
```python
# Add karma
request.user.update_karma(5, "Created new waste listing")

# Subtract karma
request.user.update_karma(-10, "Cancelled order")
```

## Proposed Karma System (Full Implementation)

### For Generators (Waste Sellers)
| Action | Karma Points | Reason |
|--------|-------------|---------|
| Create Listing | +5 | Listing new waste |
| Get Grade A | +10 | High quality waste |
| Get Grade B | +5 | Good quality waste |
| Complete Transaction | +15 | Successful sale |
| Fast Response | +3 | Reply within 24h |
| Accurate Description | +5 | Buyer confirms accuracy |
| Complete Profile | +10 | One-time bonus |

### For Buyers (Recyclers/Manufacturers)
| Action | Karma Points | Reason |
|--------|-------------|---------|
| Complete Purchase | +10 | Successful transaction |
| Leave Review | +3 | Provide feedback |
| Quick Payment | +5 | Pay within 24h |
| Bulk Order | +15 | Order > 100kg |
| Make Offer | +2 | Negotiate price |

### Penalties (Negative Karma)
| Action | Karma Points | Reason |
|--------|-------------|---------|
| Cancel Listing | -5 | After listing |
| Cancel Order | -10 | After confirmation |
| Late Delivery | -15 | Missed deadline |
| Fake Listing | -100 | Fraud attempt |
| Bad Review | -5 | Per bad review |
| Low Trust Score | -10 | Trust < 30% |

## Karma Benefits

### For High Karma Users (500+ points)
- 🏆 **Badge**: "Trusted Trader"
- ⭐ **Priority Listing**: Top of search results
- 💰 **Better Prices**: Negotiate better rates
- 🔒 **Verified Badge**: Automatic verification

### For Medium Karma Users (200-499 points)
- ✅ **Verified**: Account verified faster
- 📈 **Visibility Boost**: Higher in search
- 💬 **Direct Contact**: Message buyers/sellers

### For Low Karma Users (<200 points)
- ⚠️ **Limited**: Need approval for large orders
- 🔍 **Extra Verification**: Manual review required

## Karma Display

**Current:**
- User profile shows karma score
- Dashboard displays karma
- Visible on listings (seller karma)

**Suggested Enhancements:**
- Karma leaderboard
- Karma badges/levels
- Karma history log
- Weekly karma report

## Future Enhancements

1. **Karma Decay**: -1 point per month of inactivity
2. **Bonus Events**: Double karma weekends
3. **Referral Rewards**: +50 karma for referring new user
4. **Milestone Bonuses**: +100 at 500 karma, +200 at 1000 karma
5. **Karma Shop**: Redeem karma for premium features

## Code Locations

- **Model**: `accounts/models.py` - `CustomUser.update_karma()`
- **Usage**: `marketplace/views.py` - Line 130
- **Display**: User profile, dashboard templates

## Summary

**Current Status:**
- ✅ Karma system implemented
- ✅ +5 karma for creating listings
- ✅ Range: 0-1000
- ✅ Auto-clamps to prevent overflow

**Next Steps:**
1. Add karma for transactions
2. Implement karma penalties
3. Create karma benefits system
4. Build karma leaderboard
5. Add karma history tracking
