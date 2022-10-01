from asyncio import run
from argparse import ArgumentParser
from pyhtools.attackers.web.api.discover import APIdiscover

parser = ArgumentParser(prog='api_enum')
parser.add_argument('-u', '--url', dest='url', required=True,
                    help='base url of web application API')
parser.add_argument('-w', '--wordlist', dest='wordlist_path',
                    required=True, help='endpoints wordlist file path')
parser.add_argument('-rl', '--rate-limit', dest='rate_limit', type=int,
                    default=20, help='number of requests to send concurrently during enumeration')
parser.add_argument('-d', '--delay', dest='delay', type=float,
                    default=0.05, help='delay between requests in seconds')
parser.add_argument('-mc', '--match-codes', dest='match_codes',
                    nargs='+', type=int, default=[200, 301, 401, 403, 405], help='display or save api endpoints only matching provided http response status codes')
parser.add_argument('-o', '--output-file', dest='output_file_path', type=str,
                    help='saves results in json format to provided output file path', required=False, default=None)

args = parser.parse_args()

discoverer = APIdiscover(
    base_url=args.url,
    wordlist_path=args.wordlist_path,
    match_codes=args.match_codes,
    rate_limit=args.rate_limit,
    delay=args.delay,
    output_file_path=args.output_file_path,
)

run(
    discoverer.start()
)