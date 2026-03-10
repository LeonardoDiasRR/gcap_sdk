from gcap_sdk import Gcap

# Inicialize o cliente
gcap = Gcap()

# Faça login
print(" Tentando fazer login...")
login_result = gcap.login()
if login_result['success']:
    print("✅ Login realizado com sucesso!")
    
    # Atualizar a data da prisão do mandado específico
    print(" Atualizando data da prisão para 29/01/2026...")
    update_result = gcap.atualizar_mandado(
        mandado_id="8cc06cd1-356a-4027-87ff-a41c19134712",  # ID do mandado encontrado anteriormente
        data_prisao="2026-01-29"  # Data no formato ISO (YYYY-MM-DD)
    )
    
    if update_result['success']:
        print("✅ Data da prisão atualizada com sucesso!")
        print(f"Status HTTP: {update_result['status_code']}")
        
        # Mostrar os dados atualizados
        if update_result['data']:
            mandado_atualizado = update_result['data']
            print(f"Novo valor da data da prisão: {mandado_atualizado.get('data_prisao', 'N/A')}")
    else:
        print("❌ Erro ao atualizar data da prisão:", update_result['error'])
        
    # Logout quando terminar
    gcap.logout()
    print("✅ Logout realizado com sucesso!")
    
else:
    print("❌ Falha no login:", login_result['error'])