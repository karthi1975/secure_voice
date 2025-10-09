# 🔧 Force VAPI to Call Functions

## Problem
Luna says "Authenticating" or repeats what you say, but doesn't actually CALL the functions.

## Solution: Set Model Tool Choice

In VAPI dashboard, you need to configure the assistant to FORCE function calling:

### Option 1: Set First Message to Call Function

In your assistant settings:

1. Find **"First Message"** or **"Greeting"** section
2. Instead of text, set it to **CALL the function**
3. Some VAPI versions allow you to specify: `{"type": "function-call", "function": "home_auth"}`

### Option 2: Use Tool Choice Setting

1. Find **"Model Settings"** or **"Advanced Settings"**
2. Look for **"Tool Choice"** or **"Function Calling Mode"**
3. Set to: **"auto"** or **"required"**
4. Some versions have: **"Prefer tools"** → Enable this

### Option 3: Remove First Message Completely

Since we're using `assistant_overrides.firstMessage` from the client:

1. In VAPI dashboard assistant settings
2. Find **"First Message"** field
3. **Delete it completely** or set to empty
4. Set **"First Message Mode"** to **"Assistant waits for user"**

This way the client's override will work: `"firstMessage": "Hi! Authenticating..."`

But VAPI still needs to know to call `home_auth()` on the first turn!

### Option 4: Add to System Prompt

Try this even MORE explicit prompt:

```
You are Luna. You control devices by calling functions.

CRITICAL: You MUST call functions. Never respond without calling a function first.

FIRST MESSAGE (when conversation starts):
1. Immediately call home_auth() function with no parameters
2. After successful response, say only: "Ready"

DEVICE CONTROL:
When user mentions fan or device:
1. Call control_air_circulator(device, action) function
2. Wait for response
3. Confirm briefly (one word)

Examples:
User: "Luna" or "Hello" or ANY first message
→ Call home_auth()
→ Say "Ready"

User: "Turn on the fan"
→ Call control_air_circulator(device="power", action="turn_on")
→ Say "On"

User: "Turn off"
→ Call control_air_circulator(device="power", action="turn_off")
→ Say "Off"

User: "Medium speed"
→ Call control_air_circulator(device="speed", action="medium")
→ Say "Medium"

RULES:
- Function calls are MANDATORY
- NEVER respond with just text
- ALWAYS call the function BEFORE speaking
```

### Option 5: Check Model Configuration

Some AI models in VAPI don't support function calling well. Check:

1. Go to **Model Settings**
2. Ensure you're using: **GPT-4**, **GPT-4-turbo**, or **GPT-4o**
3. Avoid using: GPT-3.5 (less reliable with functions)

### Option 6: Test with VAPI Playground

1. In VAPI dashboard, find **"Test"** or **"Playground"**
2. Start a test conversation
3. Check the **"Messages"** or **"Debug"** panel
4. Look for function calls being made
5. If you DON'T see function calls in the debug panel, the configuration is wrong

## How to Verify It's Working

When you test, you should see in Railway logs:

```
POST /webhook?sid=xxxxx
{
  "message": {
    "type": "function-call",
    "functionCall": {
      "name": "home_auth"
    }
  }
}
```

If you see this, functions are being called! ✅

If you DON'T see `"type": "function-call"`, VAPI is not calling functions! ❌

## Quick Test

To test if functions work at all, try this in VAPI playground:

1. Send message: "test"
2. Check debug panel
3. Look for: `"tool_calls"` or `"function_call"`
4. If you see it → Functions work, prompt needs tweaking
5. If you DON'T see it → Model or settings issue

---

The most common issue is that **Tool Choice** is not set to force function calling!
