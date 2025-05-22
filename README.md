# Foninhoiuri umbrel store

Este repositório é a **minha loja comunitária de apps para o Umbrel**.

Aqui você encontrará uma seleção personalizada de aplicativos que uso e recomendo, prontos para serem instalados diretamente no seu Umbrel via App Store Comunitária.

> **💡 Dica:** Para adicionar esta loja ao seu Umbrel, vá em *App Store > Custom App Stores > Add Store* e cole o link deste repositório.

---

## Template de App Store Comunitária do Umbrel

Este repositório segue o template oficial para criar uma App Store Comunitária do Umbrel. Essas app stores adicionais permitem que desenvolvedores distribuam aplicativos sem precisar enviá-los para a [App Store Oficial do Umbrel](https://github.com/getumbrel/umbrel-apps).

---

## Aplicativos Disponíveis

| Serviço            | Imagem Docker                                           | Portas Expostas                                                                        | 
| ------------------ | ------------------------------------------------------- | -------------------------------------------------------------------------------------- | 
| **Crafty**         | `registry.gitlab.com/crafty-controller/crafty-4:latest` | `18000:8000`, `18443:8443`, `18123:8123`, `19132:19132/udp`, `25500-25565:25500-25565` | 
| **Waha**           | `ghcr.io/joaomgcd/waha:latest`                          | `3000:3000`                                                                          | 

## Outros aplicativos para referencia de porta

| Serviço            | Imagem Docker                                           | Portas Expostas                                                                        | 
| ------------------ | ------------------------------------------------------- | -------------------------------------------------------------------------------------- | 
| **n8n**            | `n8nio/n8n`                                             | `5678:5678`                                                                            | 
| **Home Assistant** | `ghcr.io/home-assistant/home-assistant:stable`          | `8123:8123`                                                                            |
| **Portainer**      | `portainer/portainer-ce`                                | `9000:9000`                                                                            | 
| **Tailscale**      | `tailscale/tailscale`                                   | `8240` (via `network_mode: host`)                                                      | 


---

## como adiconar

https://user-images.githubusercontent.com/10330103/197889452-e5cd7e96-3233-4a09-b475-94b754adc7a3.mp4
