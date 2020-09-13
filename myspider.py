import scrapy

def clear_text(text):
    return (
      text
        .replace("\t", "")
        .replace("\n", "")
        .replace("\r", "")
        .strip()
    )

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://www.ludopedia.com.br/leiloes/ultimas-24-horas']

    def parse(self, response):
        for next_page in response.css('.item-leilao a'):
            if 'id_jogo=' not in next_page.attrib['href']:
                yield response.follow(next_page, self.parse_leilao)


    def parse_leilao(self, response):
        row_info = response.css('.panel .row.row-info')
        row_info_fields = row_info.css('.col-xs-12.col-md-6')
        status_index = 0 if len(row_info_fields) == 2 else 1
        yield {
            'game': {
              'name': response.css('.title::text').get(),
              'link': row_info.css('.col-xs-12')[0].css('a').attrib['href'],
            },
            'seller': {
              'name': clear_text(row_info.css('.media-body').css('::text')[0].extract()),
              'link': row_info.css('.media-body a').attrib['href'],
              'location': clear_text(row_info.css('.media-body').css('::text')[1].extract()),
            },
            'sale_ad': {
              'status': row_info_fields[status_index].css('::text')[1].extract(),
              'end': response.css('.termino .count-down').attrib['data-dt_hr_fim'],
              'current_bid': clear_text(response.css('.vl-produto').css('::text')[0].extract()),
              "payment_methods": [
                ' '.join(
                  [clear_text(y) for y in x.css('::text').extract()]
                ) for x in response.css('.disc-list li')
              ],
              'followers': response.css('.total-follow-item').css('::text').get(),
              'views': response.css('.tot-count-view').css('::text').get(),
              'description': clear_text(response.css('#bloco-descricao-item').css('::text').get()),
              'rules': ' '.join(
                  [clear_text(y) for y in response.css('#bloco-descricao-leilao').css('::text').extract()]
                ),
            },
        }
