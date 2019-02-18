# Terraform rc

Way to share and save your terraform providers list and state.

#### install

    pip3 install git+https://github.com/egeneralov/terraformrc.git

#### example terraformrc.yml

    cat << EOF > ~/.terraformrc.yml
    version: 1
    insecure: true
    
    providers:
      - name: cloudflare
      - name: external
      - name: digitalocean
      - name: gitlab
      - name: hcloud
      - name: heroku
        version: v1.7.2_x4
      - name: helm
        version: v0.7.0_x4
      - name: local
        version: v1.1.0_x4
      - name: "null"
        version: v2.0.0_x4
      - name: external
        version: v1.0.0_x4
    
    provisioners:
      - name: ansible
        version: v2.1.1
        url: https://github.com/radekg/terraform-provisioner-ansible/releases/download/{version}/terraform-provisioner-ansible-{os}-{arch}_{version}
    EOF
    
#### apply configuration

    rcterraform -vvv


### rc.yml

- you can simple pass names of official plugins, like:
  - name: cloudflare
  - name: external
  - name: digitalocean
- or you can pass options (to any item)
  - name: ansible
    version: v2.1.1
    url: https://github.com/radekg/terraform-provisioner-ansible/releases/download/{version}/terraform-provisioner-ansible-{os}-{arch}_{version}
