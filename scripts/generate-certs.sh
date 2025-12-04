set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CERTS_DIR="$PROJECT_ROOT/certs"

mkdir -p "$CERTS_DIR"

openssl req -x509 -newkey rsa:4096 \
  -keyout "$CERTS_DIR/local.key" \
  -out "$CERTS_DIR/local.crt" \
  -days 365 -nodes \
  -subj "/CN=localhost" \
  -addext 'subjectAltName=DNS:localhost,DNS:local.test,DNS:*.local.test,DNS:api.local.test,DNS:frontend.local.test,DNS:gateway.local.test,DNS:keycloak.local.test,IP:127.0.0.1,IP:::1' \
  -addext 'basicConstraints=CA:FALSE' \
  -addext 'keyUsage=digitalSignature,keyEncipherment' \
  -addext 'extendedKeyUsage=serverAuth,clientAuth'

chmod 644 "$CERTS_DIR/local.crt"
chmod 600 "$CERTS_DIR/local.key"

echo "✓ Сертификаты успешно созданы в $CERTS_DIR/"
echo "  - local.crt"
echo "  - local.key"
echo ""
echo "Для использования сертификатов в браузере добавьте их в системное хранилище:"
echo "  macOS: Keychain Access -> Import Items -> $CERTS_DIR/local.crt -> Trust -> Always Trust"
echo "  Linux: sudo cp $CERTS_DIR/local.crt /usr/local/share/ca-certificates/ && sudo update-ca-certificates"