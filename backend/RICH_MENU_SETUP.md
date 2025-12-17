# LINE Rich Menu Setup Guide

This guide explains how to set up the LINE Rich Menu for Drive2.

## What is Rich Menu?

Rich Menu is a customizable menu interface at the bottom of the LINE chat screen. It provides quick access to frequently used functions.

## Recommended Rich Menu Design

### Layout: 2x3 Grid (6 buttons)

```
┌────────┬────────┬────────┐
│   📤   │   🔍   │   📋   │
│ Upload │ Search │  List  │
├────────┼────────┼────────┤
│   📊   │   📁   │   ℹ️   │
│ Stats  │  Coll  │  Help  │
└────────┴────────┴────────┘
```

### Button Actions

1. **Upload** (📤)
   - Type: Text
   - Text: "ส่งไฟล์มาได้เลย"
   - Purpose: Prompt user to upload files

2. **Search** (🔍)
   - Type: Text
   - Text: "/search"
   - Purpose: Quick access to search feature

3. **List** (📋)
   - Type: Text
   - Text: "/list"
   - Purpose: Show recent files

4. **Stats** (📊)
   - Type: Text
   - Text: "/stats"
   - Purpose: View storage statistics

5. **Collections** (📁)
   - Type: URI (when LIFF app is ready)
   - URI: `https://your-liff-app.com/collections`
   - Purpose: Manage collections (future)

6. **Help** (ℹ️)
   - Type: Text
   - Text: "/help"
   - Purpose: Show help menu

## How to Create Rich Menu

### Option 1: Using LINE Official Account Manager (Recommended)

1. Go to [LINE Official Account Manager](https://manager.line.biz/)
2. Select your account
3. Navigate to **Home** > **Rich menu**
4. Click **Create**
5. Follow the wizard to:
   - Upload background image (1200x810px)
   - Define action areas
   - Set actions for each button
6. Set as default menu

### Option 2: Using LINE API

You can also create Rich Menu programmatically using the LINE Messaging API.

#### Create Rich Menu with API

```bash
curl -X POST https://api.line.me/v2/bot/richmenu \
-H 'Authorization: Bearer {YOUR_CHANNEL_ACCESS_TOKEN}' \
-H 'Content-Type: application/json' \
-d '{
  "size": {
    "width": 2500,
    "height": 1686
  },
  "selected": true,
  "name": "Drive2 Main Menu",
  "chatBarText": "Menu",
  "areas": [
    {
      "bounds": {
        "x": 0,
        "y": 0,
        "width": 833,
        "height": 843
      },
      "action": {
        "type": "message",
        "text": "ส่งไฟล์มาได้เลย 📤"
      }
    },
    {
      "bounds": {
        "x": 833,
        "y": 0,
        "width": 834,
        "height": 843
      },
      "action": {
        "type": "message",
        "text": "/search"
      }
    },
    {
      "bounds": {
        "x": 1667,
        "y": 0,
        "width": 833,
        "height": 843
      },
      "action": {
        "type": "message",
        "text": "/list"
      }
    },
    {
      "bounds": {
        "x": 0,
        "y": 843,
        "width": 833,
        "height": 843
      },
      "action": {
        "type": "message",
        "text": "/stats"
      }
    },
    {
      "bounds": {
        "x": 833,
        "y": 843,
        "width": 834,
        "height": 843
      },
      "action": {
        "type": "message",
        "text": "📁 Collections (coming soon)"
      }
    },
    {
      "bounds": {
        "x": 1667,
        "y": 843,
        "width": 833,
        "height": 843
      },
      "action": {
        "type": "message",
        "text": "/help"
      }
    }
  ]
}'
```

#### Upload Rich Menu Image

After creating the Rich Menu, upload the background image:

```bash
curl -X POST https://api-data.line.me/v2/bot/richmenu/{RICH_MENU_ID}/content \
-H 'Authorization: Bearer {YOUR_CHANNEL_ACCESS_TOKEN}' \
-H 'Content-Type: image/png' \
--data-binary '@rich_menu_image.png'
```

#### Set as Default Rich Menu

```bash
curl -X POST https://api.line.me/v2/bot/user/all/richmenu/{RICH_MENU_ID} \
-H 'Authorization: Bearer {YOUR_CHANNEL_ACCESS_TOKEN}'
```

## Design Requirements

### Background Image Specifications

- **Size**: 2500 x 1686 pixels (or 1200 x 810 pixels)
- **Format**: PNG or JPEG
- **File Size**: Max 1MB
- **Color Mode**: RGB

### Design Tips

1. **Use clear icons** - Make buttons easy to understand at a glance
2. **Keep text minimal** - Icons should be self-explanatory
3. **High contrast** - Ensure buttons are clearly visible
4. **Brand colors** - Use consistent colors with your app
5. **Test on mobile** - Preview on actual device

## Example Rich Menu Image

You can create the background image using:
- **Canva** - Easy online tool with templates
- **Figma** - Professional design tool
- **Adobe Photoshop** - Full-featured editor

### Template Grid

For a 2x3 layout (2500 x 1686):
- Each button: 833 x 843 pixels
- Use guides at:
  - Vertical: 833px, 1667px
  - Horizontal: 843px

## Python Script to Create Rich Menu

```python
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuSize, RichMenuBounds, RichMenuArea, MessageAction

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')

rich_menu = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="Drive2 Main Menu",
    chat_bar_text="Menu",
    areas=[
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
            action=MessageAction(text="ส่งไฟล์มาได้เลย 📤")
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=833, y=0, width=834, height=843),
            action=MessageAction(text="/search")
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=1667, y=0, width=833, height=843),
            action=MessageAction(text="/list")
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=843, width=833, height=843),
            action=MessageAction(text="/stats")
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=833, y=843, width=834, height=843),
            action=MessageAction(text="📁 Collections")
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=1667, y=843, width=833, height=843),
            action=MessageAction(text="/help")
        )
    ]
)

# Create Rich Menu
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu)

# Upload image
with open('rich_menu_image.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

# Set as default
line_bot_api.set_default_rich_menu(rich_menu_id)

print(f"Rich Menu created: {rich_menu_id}")
```

## Testing

1. Open LINE app on your mobile device
2. Go to your bot's chat
3. Check if the Rich Menu appears at the bottom
4. Test each button to ensure correct actions

## Troubleshooting

### Rich Menu Not Showing

- Check if Rich Menu is set as default
- Verify image was uploaded successfully
- Ensure Rich Menu ID is correct
- Try closing and reopening the chat

### Buttons Not Working

- Verify action areas coordinates
- Check action type and parameters
- Ensure webhook is configured correctly
- Check bot permissions

### Image Not Displaying

- Verify image size (must be exactly 2500x1686 or 1200x810)
- Check file format (PNG or JPEG only)
- Ensure file size is under 1MB
- Try re-uploading the image

## Best Practices

1. **Keep it simple** - Don't overcrowd with too many options
2. **Update regularly** - Change menu based on user needs
3. **Test thoroughly** - Verify all actions work correctly
4. **Monitor usage** - Track which buttons are used most
5. **Iterate** - Improve based on user feedback

## Resources

- [LINE Rich Menu Documentation](https://developers.line.biz/en/docs/messaging-api/using-rich-menus/)
- [LINE Official Account Manager](https://manager.line.biz/)
- [Rich Menu Design Templates](https://www.canva.com/templates/search/line-rich-menu/)

---

Last Updated: 2025-12-17
