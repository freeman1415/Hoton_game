class_name Brand
extends RefCounted
## Фирменный стиль из брендбука (assets/Brandbook.pptx): палитра и шрифты.
## «Яркая, жизнерадостная, но не кислотная — уютная, тёплая».
## Шрифты: Montserrat — заголовки и интерфейс, Nunito — описания и диалоги (OFL, game/fonts/).
## Шрифт по умолчанию (Nunito) задан в теме проекта ui/theme.tres; заголовки —
## label.theme_type_variation = &"HeaderLabel" или Brand.HEADER_FONT в draw_string().

# Палитра брендбука (снята пипеткой со слайда «Цветовая палитра»)
const ORANGE := Color("#e48824")
const SALMON := Color("#d48464")
const BROWN := Color("#604030")
const BLUE := Color("#78b0c8")
const RED := Color("#cc5c60")
const GREEN := Color("#74b068")

# Производные для интерфейса: тёмные фоны и тёплый светлый текст
const BROWN_DARK := Color("#3a261c")
const BROWN_DEEP := Color("#2a1b14")
const CREAM := Color("#fff4e6")
const MUTED := Color("#cbb8a8")

## Выделенный пункт меню / вариант ответа
const SELECTED := ORANGE
## Обычный текст на тёмном фоне
const TEXT := CREAM

const BODY_FONT: Font = preload("res://fonts/body.tres")
const HEADER_FONT: Font = preload("res://fonts/header.tres")


## Панель в фирменном стиле: тёмно-коричневый фон, оранжевая рамка.
static func panel_style(border: Color = ORANGE) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = BROWN_DEEP
	style.border_color = border
	style.set_border_width_all(2)
	style.set_corner_radius_all(4)
	style.set_content_margin_all(10)
	return style
