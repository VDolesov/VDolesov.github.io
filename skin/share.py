SERVICES = (
    ("vkontakte", "ВКонтакте", "https://vk.com/share.php?url="),
    ("odnoklassniki", "Одноклассники", "https://connect.ok.ru/offer?url="),
    ("telegram", "Telegram", "https://t.me/share/url?url="),
    ("whatsapp", "WhatsApp", "https://wa.me/?text="),
    ("viber", "Viber", "viber://forward?text="),
)
COPY_ICON = ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" focusable="false">'
             '<path d="M10.6 13.4a1 1 0 0 1 0-1.4l3.5-3.5a1 1 0 1 1 1.4 1.4L12 13.4a1 1 0 0 1-1.4 0zm-2.1 6.4a4.5 4.5 0 0 1-3.2-7.7'
             'l2.5-2.5a1 1 0 0 1 1.4 1.4l-2.5 2.5a2.5 2.5 0 0 0 3.5 3.5l2.5-2.5a1 1 0 0 1 1.4 1.4l-2.5 2.5a4.5 4.5 0 0 1-3.1 1.4z'
             'm6.6-6.5a1 1 0 0 1-.7-1.7l2.5-2.5a2.5 2.5 0 0 0-3.5-3.5L11 8.1a1 1 0 0 1-1.4-1.4l2.5-2.5a4.5 4.5 0 0 1 6.4 6.4l-2.5 2.5'
             'a1 1 0 0 1-.9.2z"/></svg>')


def share_block(url):
    items = "".join(
        f'<li class="ya-share2__item ya-share2__item_service_{code}"><a class="ya-share2__link" href="{base}{url}" '
        f'rel="nofollow noopener" target="_blank" title="{name}" aria-label="Поделиться: {name}">'
        f'<span class="ya-share2__badge" aria-hidden="true"><span class="ya-share2__icon"></span></span>'
        f'<span class="ya-share2__title">{name}</span></a></li>'
        for code, name, base in SERVICES)
    copy = ('<li class="ya-share2__item ms-share__copy"><button type="button" class="ya-share2__link" data-ms-share-copy '
            'title="Скопировать ссылку" aria-label="Скопировать ссылку">'
            f'<span class="ya-share2__badge" aria-hidden="true">{COPY_ICON}</span>'
            '<span class="ya-share2__title">Скопировать ссылку</span></button></li>')
    return ('<div class="ya-share2 ms-share hover-block__item-wrapper"><div class="ya-share2__container ya-share2__container_size_m">'
            '<ul class="ya-share2__list ya-share2__list_direction_horizontal">' + items + copy + '</ul></div>'
            '<span class="ms-share__status" role="status" aria-live="polite"></span></div>')


SHARE_PHP = ('<?$msShareRequest = \\Bitrix\\Main\\Context::getCurrent()->getRequest();\n'
             '$msSharePort = (int)(new \\Bitrix\\Main\\Web\\Uri("http://" . \\Bitrix\\Main\\Context::getCurrent()->getServer()->getHttpHost()))->getPort();\n'
             '$msShareUrl = rawurlencode(($msShareRequest->isHttps() ? "https://" : "http://") . $msShareRequest->getHttpHost()\n'
             '    . ($msSharePort && !in_array($msSharePort, [80, 443], true) ? ":" . $msSharePort : "") . $GLOBALS["APPLICATION"]->GetCurPage(false));?>\n'
             + share_block('<?=$msShareUrl?>') + "\n")
